# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
from __future__ import annotations

import asyncio
import concurrent.futures
import json
import queue
import random
import re
import threading
import uuid
from collections import Counter, defaultdict
from typing import (
    Any,
    Iterable,
    MutableMapping,
    NamedTuple,
    Optional,
    Sequence,
    TypeVar,
)

import absl.app
import absl.flags
import aiohttp
import pyarrow
import pyarrow.compute
import ruamel.yaml
from absl import logging
from ruamel.yaml.compat import StringIO as YAMLStringIO
from typing_extensions import TypeAlias

from dyff.api import storage
from dyff.schema import ids
from dyff.schema.adapters import Adapter, HTTPData, Pipeline, create_pipeline
from dyff.schema.dataset import arrow

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_bool(
    "dryrun",
    False,
    "Scan the dataset but don't connect or make requests to the model service.",
)

absl.flags.DEFINE_string(
    "evaluation_yaml", None, "Path to a YAML file containing the Evaluation manifest."
)

absl.flags.DEFINE_bool("fail_randomly", False, "Insert random failures for testing.")


ERRORCODE_SUCCESS = 0
ERRORCODE_OUTPUT = 10
ERRORCODE_INCOMPLETE = 20


DataItem: TypeAlias = dict[str, Any]


class ItemID(NamedTuple):
    replication: str
    item_index: int


def _start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Entrypoint for the background thread that runs asyncio."""
    asyncio.set_event_loop(loop)
    loop.run_forever()


async def _rpc_inference(
    session: aiohttp.ClientSession,
    url: str,
    item_id: ItemID,
    http_data: HTTPData,
) -> tuple[ItemID, HTTPData]:
    """Post an inference request.

    Parameters:
      session: Shared ClientSession instance
      url: URL of the inference service
      item_id: The unique identifier of the instance
      http_payload: Tuple containing 'headers' and 'data' fields for the request

    Returns:
      (item_id, response_json): ``item_id`` is the same as the input item_id,
        ``response_json`` contains the response body as a JSON object.
    """
    timeout = aiohttp.ClientTimeout(total=30)
    headers = {"content-type": http_data.content_type}
    async with session.post(
        url,
        headers=headers,
        json=http_data.data,
        timeout=timeout,
        raise_for_status=True,
    ) as response:
        response_json = await response.json()
        response_data = HTTPData("application/json", response_json)
        return (item_id, response_data)


async def _throttled_rpc_inference(semaphore: asyncio.Semaphore, *args, **kwargs):
    async with semaphore:
        return await _rpc_inference(*args, **kwargs)


class _Monitor:
    def __init__(self):
        self._counts = defaultdict(int)
        self._totals = defaultdict(int)

    def event(self, name: str):
        self._counts[name] += 1
        self._totals[name] += 1

    @property
    def totals(self):
        return dict(self._totals)

    def totals_for_event(self, event: str):
        return self._totals.get(event, 0)

    async def __call__(self):
        interval_seconds = 60.0
        while True:
            self._counts.clear()
            await asyncio.sleep(interval_seconds)
            for k, v in sorted(self._counts.items()):
                logging.info(f"Monitor: {k}: {v/interval_seconds}/sec")


class RetryManager:
    def __init__(self):
        self._items: dict[ItemID, DataItem] = {}
        self._counts: MutableMapping[ItemID, int] = defaultdict(int)
        self._failures: list[ItemID] = []

    def retry(self, item_id: ItemID, item) -> bool:
        if self._items.get(item_id) is not None:
            logging.error(f"item {item_id} already queued")
            raise ValueError(f"item {item_id} already queued")
        self._counts[item_id] += 1
        if self._counts[item_id] >= 100:
            logging.error(f"item {item_id} retried 100 times; apparently unprocessable")
            self._failures.append(item_id)
            return False
        else:
            if self._counts[item_id] == 10:
                logging.warning(f"retrying {item_id} for the 10th time")
            self._items[item_id] = item
            return True

    def get(self) -> tuple[ItemID | None, DataItem | None]:
        if len(self._items) == 0:
            return None, None
        item_id = random.choice(list(self._items.keys()))
        item = self._items[item_id]
        del self._items[item_id]
        return item_id, item

    def failures(self):
        return self._failures


def _start_workers(
    *,
    num_workers: int,
    monitor: _Monitor,
    session: aiohttp.ClientSession,
    url: str,
    input_adapter: Adapter,
    output_adapter: Adapter,
    in_queue: asyncio.Queue[tuple[ItemID, DataItem]],
    out_queue: asyncio.Queue[tuple[ItemID, list[DataItem] | None]],
    retry_manager: RetryManager,
):
    """Start the asyncio inference workers."""
    tasks = []
    for i in range(num_workers):
        tasks.append(
            asyncio.create_task(
                _worker(
                    worker_id=i,
                    monitor=monitor,
                    session=session,
                    url=url,
                    input_adapter=input_adapter,
                    output_adapter=output_adapter,
                    in_queue=in_queue,
                    out_queue=out_queue,
                    retry_manager=retry_manager,
                )
            )
        )
    return tasks


async def _worker(
    *,
    worker_id: int,
    monitor: _Monitor,
    session: aiohttp.ClientSession,
    url: str,
    input_adapter: Adapter,
    output_adapter: Adapter,
    in_queue: asyncio.Queue[tuple[ItemID, DataItem]],
    out_queue: asyncio.Queue[tuple[ItemID, list[DataItem] | None]],
    retry_manager: RetryManager,
):
    """Pulls instances from the input queue and places inference results on
    the output queue. Processing is complete once ``in_queue.join()`` returns.
    """
    while True:
        item_id, item = retry_manager.get()
        if item_id is not None:
            monitor.event("retry")
        else:
            item_id, item = await in_queue.get()
            monitor.event("input")
        assert item is not None

        processed = False
        failure = False
        output_items = None
        try:
            input_data = list(input_adapter([item]))
            if len(input_data) != 1:
                raise AssertionError(
                    f"input pipeline yielded multiple values for {item_id}"
                )
            input_item = input_data[0]
            # TODO: What if the input isn't JSON?
            response_id, response_data = await _rpc_inference(
                session, url, item_id, HTTPData("application/json", input_item)
            )
            if item_id != response_id:
                raise AssertionError(
                    f"wires crossed: input {item_id} != output {response_id}"
                )
            # This throws a subclass of dyff.models.outputs.TaskOutputError
            # on verification failure
            output_items = list(output_adapter([response_data.data]))
            processed = True
        except aiohttp.ClientError as ex:
            logging.debug(f"worker {worker_id}: ClientError; retrying: {item_id}")
            monitor.event(type(ex).__name__)
            # Retry
            failure = not retry_manager.retry(item_id, item)
            # Prevent spamming failed connections if the InferenceServices are
            # still starting
            await asyncio.sleep(30)
        except asyncio.exceptions.TimeoutError:
            logging.debug(f"worker {worker_id}: TimeoutError; retrying: {item_id}")
            monitor.event("TimeoutError")
            # Retry
            failure = not retry_manager.retry(item_id, item)
        except Exception as ex:
            event_name = type(ex).__name__
            logging.exception(
                f"worker {worker_id}: {event_name} (fatal): {item_id}: |{response_data}|"
            )
            failure = True
        finally:
            if failure:
                monitor.event("Failure")
                # Failure means there's something unrecoverably wrong with the
                # input instance. (item_id, None) indicates failed inference.
                await out_queue.put((item_id, None))
                in_queue.task_done()
            elif processed:
                await out_queue.put((item_id, output_items))
                in_queue.task_done()
                monitor.event("output")


async def _copy_output(async_queue: asyncio.Queue, sync_queue: queue.Queue):
    """Copies output from the asyncio queue to the synchronous queue. All of
    the output has been copied once ``await async_queue.join()`` returns.
    """
    pending_output = None
    while True:
        if pending_output is None:
            pending_output = await async_queue.get()
            assert pending_output is not None

        try:
            sync_queue.put_nowait(pending_output)
        except queue.Full:
            await asyncio.sleep(0.1)
        else:
            pending_output = None
            async_queue.task_done()


async def _async_main(
    *,
    num_workers: int,
    url: str,
    input_adapter: Adapter,
    output_adapter: Adapter,
    in_queue: queue.Queue[tuple[ItemID, DataItem] | None],
    out_queue: queue.Queue[tuple[ItemID | None, list[DataItem] | None]],
):
    """The main function of the asyncio thread. Spawns workers and output
    task and waits for them to complete.

    Parameters:
      num_workers: Number of worker tasks
      url: URL of the inference service
      in_queue: Instances for inference. Input is complete when
        ``in_queue.get()`` returns the sentinel value ``None``.
      out_queue: Inference results. Inference is complete when
        ``out_queue.get()`` returns the sentinel value ``(None, None)``.
    """
    # Kubernetes does not load-balance persistent connections properly;
    # force_close=True makes them not persistent.
    # See: https://stackoverflow.com/a/71216872
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(force_close=True)
    ) as session:
        # Propagate input queue limits
        work_queue: asyncio.Queue[tuple[ItemID, DataItem]] = asyncio.Queue(
            in_queue.maxsize
        )
        result_queue: asyncio.Queue[tuple[ItemID, list[DataItem] | None]] = (
            asyncio.Queue()
        )
        retry_manager = RetryManager()
        monitor = _Monitor()
        processed_indices: set[ItemID] = set()

        worker_tasks = []
        worker_tasks.append(asyncio.create_task(_copy_output(result_queue, out_queue)))
        worker_tasks.append(asyncio.create_task(monitor()))
        worker_tasks.extend(
            _start_workers(
                num_workers=num_workers,
                monitor=monitor,
                session=session,
                url=url,
                input_adapter=input_adapter,
                output_adapter=output_adapter,
                in_queue=work_queue,
                out_queue=result_queue,
                retry_manager=retry_manager,
            )
        )

        while True:
            try:
                work_item = in_queue.get_nowait()
                if work_item is None:  # sentinel
                    break
                item_id, item = work_item
                if item_id in processed_indices:
                    logging.error(f"duplicate item {item_id} in in_queue")
                    monitor.event("DuplicateWorkItem")
                else:
                    processed_indices.add(item_id)
                    await work_queue.put((item_id, item))
            except queue.Empty:
                await asyncio.sleep(0.1)

        # Wait for output
        logging.info("joining work_queue")
        await work_queue.join()
        logging.info("joining result_queue")
        await result_queue.join()
        # Cancel tasks
        logging.info("cancelling worker_tasks")
        for task in worker_tasks:
            task.cancel()
        logging.info("waiting for canceled tasks")
        await asyncio.gather(*worker_tasks, return_exceptions=True)
        logging.info("putting sentinel on out_queue")
        out_queue.put((None, None))  # sentinel

        logging.info(f"Monitor event totals: {monitor.totals}")
        if monitor.totals_for_event("input") != monitor.totals_for_event("output"):
            logging.error("Monitor: 'input' != 'output'")
        failures = retry_manager.failures()
        if len(failures) > 0:
            logging.error(f"failed indices: {failures}")


def _output_thread(
    *,
    out_queue: queue.Queue[tuple[ItemID | None, list[DataItem] | None]],
    output_path: str,
    output_schema: pyarrow.Schema,
    batch_size: int = 1000,
):
    """Entry point for the thread that writes PyArrow output. Assumes that
    inference is finished if ``out_queue.get()`` returns the sentinel
    ``(None, None)``.
    """

    def batch_generator(output_schema):
        processed = set()
        batch_idx = 0
        result_batch = []
        while True:
            item_id, responses = out_queue.get()
            if item_id is None:  # sentinel
                logging.info(f"output {len(processed)} unique indices")
                break
            elif responses is None:
                logging.error(f"inference failed: item {item_id}")
                continue

            if item_id in processed:
                logging.error(f"duplicate item {item_id} in out_queue")
                continue
            else:
                processed.add(item_id)

            logging.debug(f"finished {item_id}: {len(responses)} responses")
            for i, response in enumerate(responses):
                response["_response_index_"] = i
            response_record = {
                "_replication_": item_id.replication,
                "_index_": item_id.item_index,
                "responses": responses,
            }
            result_batch.append(response_record)

            if len(result_batch) >= batch_size:
                logging.info(f"finished batch {batch_idx}")
                batch_idx += 1
                yield pyarrow.RecordBatch.from_pylist(
                    result_batch, schema=output_schema
                )
                result_batch = []
        if len(result_batch) > 0:
            logging.info(f"finished batch {batch_idx} (final batch)")
            yield pyarrow.RecordBatch.from_pylist(result_batch, schema=output_schema)

    # Note: We don't partition the outputs because that undermines our goal of
    # writing small chunks frequently to preserve progress. We can re-partition
    # in verify_evaluation_output if desired.
    arrow.write_dataset(
        batch_generator(output_schema),
        output_path=output_path,
        feature_schema=output_schema,
        # Force frequent writes so we don't lose progress
        max_rows_per_file=batch_size,
        # pyarrow.lib.ArrowInvalid: max_rows_per_group must be less than or equal to max_rows_per_file
        max_rows_per_group=batch_size,
        # Use UUIDs so that we never overwrite old data. On a restart, we read
        # all the data that's already persisted and skip those indices.
        basename_template=f"{uuid.uuid4()}.{{i}}.parquet",
    )


class _MissingItemPredicate:
    def __init__(self, *, not_missing: Optional[set[ItemID]] = None):
        self._not_missing = not_missing or set()

    def __call__(self, item_id: ItemID) -> bool:
        return item_id not in self._not_missing


def _dataset_fragments(path: str) -> list[str]:
    """Returns a list of full GCS paths to each dataset fragment for which
    ``path`` is a prefix. Remember that GCS "directory" list operations are
    always recursive because they're not really "directories".
    """
    # FIXME: Should open the .dyff/artifacts.json file to get the artifact list,
    # but this is not created for evaluation output datasets currently.
    objects = storage.list_dir(path)
    pattern = r"/[^/]*\.parquet$"
    fragments = [obj for obj in objects if re.search(pattern, obj)]
    return fragments


def _missing_item_predicate(output_path: str):
    try:
        # There is a race between output_path creation and reading the
        # dataset here. If the directory has been created, we open an empty
        # dataset and PyArrow throws an exception because there is no _index_
        # column. Thus, we need to check for an empty dataset.
        fragments = _dataset_fragments(output_path)
        if len(fragments) == 0:
            return _MissingItemPredicate()
        outputs = arrow.open_dataset(output_path)
        not_missing: list[ItemID] = []
        for b in outputs.to_batches(columns=["_replication_", "_index_"]):
            not_missing.extend(
                ItemID(replication=x["_replication_"], item_index=x["_index_"])
                for x in b.to_pylist()
            )
        logging.info(f"found {len(not_missing)} outputs in {output_path}")
        counts = Counter(not_missing)
        duplicates = [k for k, v in counts.items() if v > 1]
        if len(duplicates) > 0:
            logging.error(f"duplicates in outputs: {duplicates}")
            raise ValueError("duplicates in outputs")
        return _MissingItemPredicate(not_missing=set(not_missing))
    except FileNotFoundError:
        return _MissingItemPredicate()


def _inference_service_address(evaluation_yaml) -> str:
    name = evaluation_yaml["metadata"]["name"]
    namespace = evaluation_yaml["metadata"]["namespace"]
    return f"http://{name}-infer.{namespace}:80"


def _load_pipeline(pipeline_spec: list[dict]) -> Pipeline:
    pipeline_spec = [
        {
            "kind": adapter_spec["kind"],
            "configuration": json.loads(adapter_spec["configuration"]),
        }
        for adapter_spec in pipeline_spec
    ]
    return create_pipeline(pipeline_spec)


def main(_unused_argv: Sequence[str]) -> Optional[int]:
    logging.set_verbosity(logging.DEBUG)

    yaml = ruamel.yaml.YAML()
    with open(FLAGS.evaluation_yaml, "r") as fin:
        evaluation = yaml.load(fin)
    yaml_string = YAMLStringIO()
    yaml.dump(evaluation, yaml_string)
    logging.info(f"evaluation_yaml:\n{yaml_string.getvalue()}")

    dataset = evaluation["spec"]["dataset"]
    # TODO: We allow specifying a different path for dataset uploads, so we
    # should allow loading them from an alternative path here. Actually,
    # should we expand Dataset to include its storage location?
    dataset_path = storage.paths.dataset_root(dataset)
    ds = arrow.open_dataset(dataset_path)
    logging.info(f"input dataset: {dataset}")

    interface = evaluation["spec"]["interface"]
    inference_endpoint = interface["endpoint"]
    output_schema = arrow.decode_schema(interface["outputSchema"]["arrowSchema"])
    input_pipeline = _load_pipeline(interface["inputPipeline"])
    output_pipeline = _load_pipeline(interface["outputPipeline"])

    # defaults
    batch_size = 1000
    filter_expression = None
    # if (dataset_config := evaluation["spec"].get("datasetConfiguration")) is not None:
    #     if (filters := dataset_config.get("filters")) is not None:
    #         filter_expression = parse_dataset_filters(filters)
    #         logging.info(f"dataset filter: {filter_expression}")
    #     batch_size = dataset_config.get("batchSize", batch_size)

    input_rows = ds.scanner(filter=filter_expression).count_rows()
    logging.info(f"input dataset: {input_rows} rows")

    evaluation_id = evaluation["spec"]["id"]
    replications: int = evaluation["spec"]["replications"]
    replication_ids = [
        ids.replication_id(evaluation_id, i) for i in range(replications)
    ]

    output_path = storage.paths.outputs_raw(evaluation_id)
    missing = _missing_item_predicate(output_path)
    processed_items = set()

    # defaults
    # FIXME: These should be defaults in the CRD, not here
    inference_service_replicas = evaluation["spec"]["inferenceSession"].get(
        "replicas", 1
    )
    workers_per_replica = evaluation["spec"].get("workersPerReplica", 2)
    num_workers = inference_service_replicas * workers_per_replica

    service_address = _inference_service_address(evaluation)
    service_url = f"{service_address}/{inference_endpoint}"

    # Limit input queue to avoid memory limits
    work_queue: queue.Queue[tuple[ItemID, DataItem] | None] = queue.Queue(
        maxsize=(4 * batch_size)
    )
    result_queue: queue.Queue[tuple[ItemID | None, list[DataItem] | None]] = (
        queue.Queue()
    )

    logging.info("starting asyncio thread")
    asyncio_loop = asyncio.new_event_loop()
    async_thread = threading.Thread(
        target=_start_background_loop, args=(asyncio_loop,), daemon=True
    )
    async_thread.start()
    logging.info("launching _async_main")
    async_main = asyncio.run_coroutine_threadsafe(
        _async_main(
            num_workers=num_workers,
            url=service_url,
            input_adapter=input_pipeline,
            output_adapter=output_pipeline,
            in_queue=work_queue,
            out_queue=result_queue,
        ),
        asyncio_loop,
    )

    output_error = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # Doing this with concurrent.futures is the simplest way to propagate
        # exceptions from the thread.
        # See: https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example
        logging.info("starting output thread")
        output_future = executor.submit(
            _output_thread,
            out_queue=result_queue,
            output_path=output_path,
            output_schema=output_schema,
            batch_size=batch_size,
        )

        T = TypeVar("T")

        def shuffle(items: Iterable[T], buffer_size: int = 10000) -> Iterable[T]:
            buffer: list[T] = []
            for item in items:
                if len(buffer) == buffer_size:
                    idx = random.randrange(buffer_size)
                    yield buffer[idx]
                    buffer[idx] = item
                else:
                    buffer.append(item)
            # Yield remaining items
            random.shuffle(buffer)
            yield from buffer

        def work_items() -> Iterable[tuple[ItemID, DataItem]]:
            for record_batch in ds.to_batches(
                batch_size=batch_size, filter=filter_expression
            ):
                for record in record_batch.to_pylist():
                    index = record["_index_"]
                    for replication_id in replication_ids:
                        item_id = ItemID(replication=replication_id, item_index=index)
                        if missing(item_id):
                            logging.debug(f"enqueue {item_id}")
                            yield (item_id, record)
                        processed_items.add(item_id)

        logging.info("processing dataset")
        for work_item in shuffle(work_items()):
            work_queue.put(work_item)
        work_queue.put(None)  # sentinel

        logging.info("waiting for output_thread")
        for future in concurrent.futures.as_completed([output_future]):
            try:
                future.result()
            except Exception:
                logging.exception("output error")
                output_error = True
        # Thread gets joined on context exit
        logging.info("joining output_thread")

    logging.info("waiting for async_main")
    async_main.result()
    logging.info("stopping asyncio_loop")
    asyncio_loop.stop()
    # This join never returns, which makes me nervous because I think that it
    # ought to return. Removing it doesn't seem to cause problems, though.
    # logging.info("joining async_thread")
    # async_thread.join()

    if output_error:
        return ERRORCODE_OUTPUT
    else:
        N = input_rows * replications
        logging.info("verifying output")
        output_rows = arrow.open_dataset(output_path).count_rows()

        if output_rows != N:
            logging.error(
                f"incomplete output: output_rows {output_rows} != input_rows*replications {N}"
            )
            return ERRORCODE_INCOMPLETE
        elif len(processed_items) != N:
            logging.error(
                f"incomplete output: processed_items {len(processed_items)}"
                f" != input_rows*replications {N}"
            )
            return ERRORCODE_INCOMPLETE
        else:
            logging.info("Alles gut!")
            return ERRORCODE_SUCCESS


if __name__ == "__main__":
    absl.app.run(main)
