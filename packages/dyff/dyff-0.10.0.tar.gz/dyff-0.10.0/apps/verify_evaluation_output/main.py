# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
import math
from collections import Counter
from typing import NamedTuple, Optional

import absl.app
import absl.flags
import pyarrow
import ruamel.yaml
from absl import logging
from ruamel.yaml.compat import StringIO as YAMLStringIO

from dyff.api import storage
from dyff.schema import ids
from dyff.schema.dataset import arrow

# -----------------------------------------------------------------------------

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string(
    "evaluation_yaml", None, "Path to a YAML file containing the Evaluation manifest."
)


# Return codes should be combined with bitwise-or
RETURNCODE_SUCCESS = 0
RETURNCODE_OUTPUT_ERROR = 1 << 0
RETURNCODE_MISSING = 1 << 1
RETURNCODE_DUPLICATES = 1 << 2

# -----------------------------------------------------------------------------


class ItemID(NamedTuple):
    replication: str
    item_index: int


def verify_output(evaluation, *, repartition: bool) -> int:
    evaluation_id = evaluation["spec"]["id"]
    dataset = evaluation["spec"]["dataset"]
    replications: int = evaluation["spec"]["replications"]

    outputs_dataset = arrow.open_dataset(storage.paths.outputs_raw(evaluation_id))
    feature_schema = outputs_dataset.schema
    num_rows = outputs_dataset.count_rows()
    output_size = storage.storage_size(storage.paths.outputs_raw(evaluation_id))
    size_MBi = output_size / (1000 * 1024)
    MBi_per_row = size_MBi / num_rows
    # Target is 100MBi per file
    n = 100.0 / MBi_per_row
    # Nice round number -- smallest power of 2 s.t. n * MBi_per_row >= 100
    rows_per_file = int(math.pow(2, math.ceil(math.log2(n))))
    logging.info(
        f"rows: {num_rows}; size (MBi): {size_MBi}; rows_per_file: {rows_per_file}"
    )

    input_dataset = arrow.open_dataset(storage.paths.dataset_root(dataset))
    filter_expression = None
    # if (dataset_config := evaluation["spec"].get("datasetConfiguration")) is not None:
    #     if (filters := dataset_config.get("filters")) is not None:
    #         filter_expression = parse_dataset_filters(filters)
    #         logging.info(f"dataset filter: {filter_expression}")
    input_indices = []
    for b in input_dataset.to_batches(columns=["_index_"], filter=filter_expression):
        input_indices.extend(b.to_pandas()["_index_"])
    unique_input_indices = set(input_indices)
    assert len(unique_input_indices) == len(
        input_indices
    ), "duplicate indices in input dataset"
    logging.info(f"input dataset: {len(unique_input_indices)} unique indices")
    replication_ids = [
        ids.replication_id(evaluation_id, i) for i in range(replications)
    ]
    input_items = []
    for index in input_indices:
        for replication in replication_ids:
            input_items.append(ItemID(replication=replication, item_index=index))

    partition_keys = evaluation["spec"].get("outputDatasetPartitions")
    if partition_keys:
        # If these fields are present, we want to represent them as partitions
        partition_fields = []
        for partition_key in partition_keys:
            field_index = feature_schema.get_field_index(partition_key)
            if field_index != -1:
                partition_fields.append(feature_schema.field(field_index))
        partition_schema = (
            pyarrow.schema(partition_fields) if partition_fields else None
        )
    else:
        # FIXME: That PyArrow bug seems to be back where it doesn't correctly
        # populate .partitioning.schema when there isn't actually a partitioning
        partition_schema = None
        # Else keep the partitioning from the unverified outputs
        # partition_schema = (
        #     outputs_dataset.partitioning and outputs_dataset.partitioning.schema
        # )
    logging.info(f"feature_schema:\n{feature_schema}")
    logging.info(f"partition_schema:\n{partition_schema}")

    processed: list[ItemID] = []
    errors: list[ItemID] = []

    def output_generator(outputs_dataset, processed: list[ItemID] = processed):
        for b in outputs_dataset.to_batches():
            batch = []
            for item in b.to_pylist():
                # TODO: We're not doing any content checking anymore because
                # all we have is the arrow schema
                item_id = ItemID(
                    replication=item["_replication_"], item_index=item["_index_"]
                )
                batch.append(item)
                processed.append(item_id)
                if len(processed) % 100000 == 0:
                    logging.info(f"processed {len(processed)} items")
            yield pyarrow.RecordBatch.from_pylist(batch, schema=feature_schema)

    outputs_dataset = arrow.open_dataset(storage.paths.outputs_raw(evaluation_id))

    arrow.write_dataset(
        output_generator(outputs_dataset),
        output_path=storage.paths.outputs_verified(evaluation_id),
        feature_schema=feature_schema,
        partition_schema=partition_schema,
        max_rows_per_file=rows_per_file,
        # max_rows_per_group must be less than or equal to max_rows_per_file
        max_rows_per_group=rows_per_file,
    )

    return_code = 0
    logging.info(f"final: {len(processed)} items; {len(set(processed))} unique")
    if len(errors) > 0:
        logging.error(f"found output errors: {errors}")
        return_code |= RETURNCODE_OUTPUT_ERROR
    counts = Counter(processed)
    duplicates = [k for k, v in counts.items() if v > 1]
    if len(duplicates) > 0:
        logging.error(f"found duplicate items: {duplicates}")
        return_code |= RETURNCODE_DUPLICATES
    missing = set(input_items).difference(set(processed))
    if len(missing) > 0:
        logging.error(f"missing items: {missing}")
        return_code |= RETURNCODE_MISSING
    return return_code


def main(_unused_argv: list[str]) -> Optional[int]:
    logging.set_verbosity(logging.INFO)

    yaml = ruamel.yaml.YAML()
    with open(FLAGS.evaluation_yaml, "r") as fin:
        evaluation = yaml.load(fin)
    yaml_string = YAMLStringIO()
    yaml.dump(evaluation, yaml_string)
    logging.info(f"evaluation_yaml:\n{yaml_string.getvalue()}")

    return verify_output(evaluation, repartition=True)


if __name__ == "__main__":
    absl.app.run(main)
