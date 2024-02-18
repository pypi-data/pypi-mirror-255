# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
from __future__ import annotations

import datetime
import json
from collections import defaultdict
from typing import Dict, Iterable, List, NamedTuple, Optional, TypeVar

import absl.app
import absl.flags
import confluent_kafka as kafka
import kubernetes.client.exceptions
import networkx
import pydantic
import rocksdict
from absl import logging

from dyff.api.backend.kafka.command import (
    deserialize_entity,
    deserialize_id,
    serialize_id,
    serialize_value,
)
from dyff.api.typing import YAMLObject
from dyff.core.config import config
from dyff.orchestrator.k8s import conditions, load_config, resources
from dyff.schema.platform import (
    Dataset,
    DyffEntity,
    DyffEntityType,
    Entities,
    EntityStatus,
    EntityStatusReason,
    is_status_success,
    is_status_terminal,
)

from . import crd

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string("namespace", "default", "k8s namespace")

absl.flags.DEFINE_bool("once", False, "Run the polling loop once, then exit")
absl.flags.DEFINE_bool(
    "from_beginning",
    False,
    "Consume the workflows.state topic from the beginning (i.e., reset the commit offset)",
)
absl.flags.DEFINE_bool(
    "disable_kafka_producer", False, "Print log messages but don't modify state"
)
absl.flags.DEFINE_bool(
    "disable_kubernetes_actions",
    False,
    "Don't make changes in Kubernetes. Still update the database and produce messages.",
)
absl.flags.DEFINE_bool("disable_quotas", False, "Don't enforce job quotas")

absl.flags.DEFINE_string("local_db_path", None, "Path to local DB files")

absl.flags.DEFINE_string("workflows_events_topic", None, "Workflows events topic")
absl.flags.DEFINE_string("workflows_state_topic", None, "Workflows state topic")
absl.flags.DEFINE_string("kafka_bootstrap_servers", None, "Address of bootstrap server")

absl.flags.DEFINE_bool(
    "debug_ignore_bad_messages",
    False,
    "Swallow exceptions from process_message(). Useful for testing where there are messages with obsolete schemas still in the topic.",
)
absl.flags.DEFINE_bool(
    "debug_ignore_missing_dependencies",
    False,
    "Assume that dependencies that are not in the dependency graph are in a Ready status.",
)


# FIXME: Should have per-account quotas stored in the database
quotas: dict[str, int] = {
    Entities.Audit: 8,
    Entities.Dataset: 1,
    Entities.Evaluation: 4,
    Entities.InferenceService: 4,
    Entities.InferenceSession: 4,
    Entities.Model: 4,
    Entities.Report: 8,
}


class LocalDBWriteBatch:
    """Represents a batch write operation.

    Apply the batch write with ``LocalDB.write_batch()``. The batch write happens
    in a single transaction.
    """

    def __init__(self):
        self.batch = rocksdict.WriteBatch(raw_mode=True)

    def put_entity(self, id: str, entity: DyffEntity):
        """Add an entity put operation to the batch."""
        self.batch.put(id.encode("utf-8"), entity.json().encode("utf-8"))

    def put_dependency_graph(self, dependency_graph: DependencyGraph):
        """Add a DependencyGraph put operation to the batch."""
        self.batch.put(
            "__dependency_graph".encode("utf-8"), dependency_graph.serialize()
        )


class LocalDB:
    """A local database that stores the Orchestrator's snapshot of the state of
    all the workflow entities in the system as well as the current dependency
    graph.
    """

    def __init__(self, db_path: str):
        self.db = rocksdict.Rdict(db_path, options=rocksdict.Options(raw_mode=True))

    def close(self):
        if self.db:
            self.db.close()

    def __getitem__(self, id: str) -> Optional[DyffEntityType]:
        return self.get_entity(id)

    def get_entity(self, id: str) -> Optional[DyffEntityType]:
        """Get an entity by ID."""
        raw = self.db.get(id.encode("utf-8"))
        return raw and deserialize_entity(raw)

    def get_dependency_graph(self) -> DependencyGraph:
        """Get the dependency graph."""
        graph_bytes: Optional[bytes] = self.db.get("__dependency_graph".encode("utf-8"))
        graph = DependencyGraph()
        if graph_bytes is None:
            # This doesn't need to be part of a batch transaction because the
            # graph is empty.
            self.db.put("__dependency_graph".encode("utf-8"), graph.serialize())
        else:
            graph.deserialize(graph_bytes)
        return graph

    def write_batch(self, batch: LocalDBWriteBatch):
        """Execute a batch write.

        The batch write happens in a single transaction, so it either totally
        succeeds or it fails without changing the DB state.
        """
        return self.db.write(batch.batch)


DyffEntityT = TypeVar("DyffEntityT", bound=DyffEntity)


class DependencyGraph:
    """A directed graph representing dependencies among workflows."""

    def __init__(self):
        self._graph = networkx.DiGraph()

    def add_created(self, db: LocalDB, entity: DyffEntityT) -> YAMLObject:
        """Add a newly-created workflow to the graph.

        Returns either the original entity unchanged, or a copy of the entity with
        its .status and .reason fields set appropriately. The returned entity
        may have .reason == UnsatisfiedDependency if it is waiting for a dependency
        to complete, or .status == Error and .reason == FailedDependency if one
        of its dependencies is already in a failure state.
        """
        assert entity.status == EntityStatus.created
        assert entity.reason == None
        edges = []
        update = {}
        for dependency_id in entity.dependencies():
            dependency = db.get_entity(dependency_id)
            if dependency is None:
                if not FLAGS.debug_ignore_missing_dependencies:
                    edges.append((dependency_id, entity.id))
                    update = {
                        "status": EntityStatus.created,
                        "reason": EntityStatusReason.unsatisfied_dependency,
                    }
            elif not is_status_terminal(dependency.status):
                edges.append((dependency_id, entity.id))
                update = {
                    "status": EntityStatus.created,
                    "reason": EntityStatusReason.unsatisfied_dependency,
                }
            elif not is_status_success(dependency.status):
                # We treat this as an unrecoverable error
                update = {
                    "status": EntityStatus.error,
                    "reason": EntityStatusReason.failed_dependency,
                }
                break
        else:
            # Delay graph changes until here in case there's a failed dependency
            self._graph.add_node(entity.id)
            self._graph.add_edges_from(edges)
        return update

    def on_workflow_termination(
        self, db: LocalDB, entity: DyffEntityType
    ) -> List[DyffEntityType]:
        """Update the graph when a workflow terminates.

        Returns a list of entities whose .status and/or .reason also changed as
        a result of the termination. The returned list *does not* include the
        ``entity`` argument.

        Currently, the only reason that other entities' state
        would change is if the workflow terminated in a failure state and other
        workflows depend on it.
        """

        def propagate_failure(root: DyffEntityType) -> List[DyffEntityType]:
            failures: List[DyffEntityType] = []
            dfs_stack: List[str] = [root.id]
            visited = set()
            while dfs_stack:
                current_node = dfs_stack.pop()
                if current_node in visited:
                    continue
                visited.add(current_node)
                dfs_stack.extend(self._graph.successors(current_node))
                if current_node != root.id:
                    # Don't update the status of the root entity, to preserve its .reason
                    current_entity = db.get_entity(current_node)
                    assert current_entity is not None
                    update = {
                        "status": EntityStatus.error,
                        "reason": EntityStatusReason.failed_dependency,
                    }
                    failures.append(current_entity.copy(update=update))

            for failed_entity in failures:
                self._graph.remove_node(failed_entity.id)
            return failures

        assert is_status_terminal(entity.status)
        if not self._graph.has_node(entity.id):
            # If we receive a duplicate message, we may have already removed the node
            return []

        failures = []
        if not is_status_success(entity.status):
            failures = propagate_failure(entity)
        self._graph.remove_node(entity.id)
        return failures

    def schedulable_entities(self) -> Iterable[str]:
        """Yields the .id's of entities in the graph that have all of their
        dependencies satisfied.
        """
        yield from (id for id, in_degree in self._graph.in_degree() if in_degree == 0)

    def deserialize(self, data: bytes):
        """Restore the graph structure from its serialized representation."""
        graph_data = json.loads(data.decode("utf-8"))
        self._graph = networkx.readwrite.json_graph.adjacency_graph(
            graph_data, directed=True, multigraph=False
        )

    def serialize(self) -> bytes:
        """Returns the serialized representation of the graph structure."""
        graph_data = networkx.readwrite.json_graph.adjacency_data(self._graph)
        return json.dumps(graph_data).encode("utf-8")

    def __str__(self) -> str:
        graph_data = networkx.readwrite.json_graph.adjacency_data(self._graph)
        return json.dumps(graph_data, indent=2)


class JobQueueItem(NamedTuple):
    # This should be 0 for admitted entities and 1 otherwise, so that admitted
    # entities are sorted before not-admitted entities.
    waiting: bool
    creationTime: datetime.datetime
    # .id is included as a tiebreaker in case .creationTime's are equal, since
    # DyffEntity's don't have an ordering defined
    id: str
    entity: DyffEntityType

    @staticmethod
    def from_entity(entity: DyffEntityType) -> JobQueueItem:
        return JobQueueItem(
            waiting=(entity.status != EntityStatus.admitted),
            creationTime=entity.creationTime,
            id=entity.id,
            entity=entity,
        )


class Orchestrator:
    """Manages Dyff entities that are in the ``Created`` status until advancing
    them to the ``Admitted`` status.

    The Orchestrator maintains a local snapshot of entity state in a RocksDB
    instance. Incoming Kafka messages update the local snapshot. Periodically,
    the Orchestrator runs a scheduling task using its local snapshot of entity
    state.

    The Orchestrator also maintains a dependency graph, which is also stored
    in RocksDB. This records which workflows are waiting on dependencies to
    complete.
    """

    def __init__(
        self,
        *,
        local_db_path: str,
        workflows_events_topic: str,
        workflows_state_topic: str,
        kafka_bootstrap_servers: str,
        disable_kafka_producer: bool = False,
        disable_kubernetes_actions: bool = False,
    ):
        self.workflows_events_topic = workflows_events_topic
        self.workflows_state_topic = workflows_state_topic

        self.db = LocalDB(local_db_path)
        self.dependency_graph = self.db.get_dependency_graph()
        self.disable_kafka_producer = disable_kafka_producer
        self.disable_kubernetes_actions = disable_kubernetes_actions

        consumer_config = {
            "bootstrap.servers": kafka_bootstrap_servers,
            "group.id": "dyff.system.orchestrator",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "on_commit": self.on_commit,
        }
        self.consumer = kafka.Consumer(consumer_config)

        producer_config = {
            "bootstrap.servers": kafka_bootstrap_servers,
            "client.id": "dyff.system.orchestrator",
            # This is the default, but setting it explicitly means an exception will
            # be raised if other config settings are in conflict.
            "enable.idempotence": True,
        }
        self.producer = kafka.Producer(producer_config)

        self.log_debug_db()

    def log_debug_db(self):
        if logging.level_debug():
            db_lines = []
            for k, v in self.db.db.items():
                db_lines.append(f"{k}: {v}")
            db_str = "\n".join(db_lines)
            logging.debug(f"LocalDB:\n{db_str}")
            logging.debug(f"DependencyGraph:\n{self.dependency_graph}")

    def close(self):
        if self.producer:
            self.producer.flush()
        if self.consumer:
            self.consumer.close()
        if self.db:
            self.db.close()

    def _admit_entity(self, entity: DyffEntityT, manifest) -> YAMLObject:
        assert entity.status == EntityStatus.created

        conditions_list = conditions.ConditionsList()
        conditions_list.set(
            EntityStatus.admitted, status=conditions.ConditionStatus.true
        )
        manifest["status"] = {"conditions": conditions_list.conditions_list}

        if not self.disable_kubernetes_actions:
            resources.create_resource(entity.kind, manifest, namespace=FLAGS.namespace)
        logging.info(f"created {manifest['metadata']['name']}")
        return {"status": EntityStatus.admitted, "reason": None}

    def on_produce_acknowledged(self, error, msg):
        if error:
            logging.error(f"delivery failed: {error}")
        else:
            logging.debug(f"message produced: {msg}")

    def on_commit(self, error, partitions):
        if error:
            logging.error(f"commit failed: {error}")
        else:
            logging.debug(f"committed partition offsets: {partitions}")

    def create_k8s_workflow(self, entity: DyffEntityType) -> Optional[YAMLObject]:
        try:
            manifest = crd.manifest(entity)
            if manifest is not None:
                return self._admit_entity(entity, manifest)
            else:
                logging.debug(f"Nothing to do for {entity.kind} {entity.id}")
                if isinstance(entity, Dataset):
                    # No status change: user needs to upload data to and then
                    # manually indicate Ready
                    return None
                else:
                    return {"status": EntityStatus.ready, "reason": None}
        except Exception:
            logging.exception(
                f"workflow {entity.kind} {entity.id}: failed to create k8s manifest"
            )
            # TODO: Make an enum entry for SchemaError reason (?)
            return {"status": EntityStatus.failed, "reason": "SchemaError"}

    def delete_k8s_workflow(self, entity: DyffEntity):
        name = resources.object_name(entity.kind, entity.id)
        if not self.disable_kubernetes_actions:
            resources.delete_resource(entity.kind, name, namespace=FLAGS.namespace)
        logging.info(f"deleted {name}")

    def produce_event(self, entity_id: str, update: YAMLObject):
        logging.debug(f"produce: {entity_id}: {update}")
        if not self.disable_kafka_producer:
            self.producer.produce(
                self.workflows_events_topic,
                key=serialize_id(entity_id),
                value=serialize_value(update),
                callback=self.on_produce_acknowledged,
            )

    def maybe_admit_more_workflows(self) -> None:
        """Scan the entire dependency graph for workflows whose dependencies are
        satisfied, and either admit them or place them in the .reason == QuotaLimit
        state as appropriate.

        Note that we do not modify the local db here; instead we send events
        and let the updates happen via the event processing logic. This is
        because events might change the dependency graph and we want to keep
        those updates in one place for simplicity.
        """
        # account -> kind -> [JobQueueItem]
        schedulable_entities: Dict[str, Dict[str, List[JobQueueItem]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for schedulable_id in self.dependency_graph.schedulable_entities():
            schedulable = self.db.get_entity(schedulable_id)
            if schedulable is not None:
                # Entity can be None if it is mentioned as a dependency but we haven't
                # received the Created message yet
                schedulable_entities[schedulable.account][schedulable.kind].append(
                    JobQueueItem.from_entity(schedulable)
                )

        for account, kinds in schedulable_entities.items():
            for kind, entities in kinds.items():
                # See JobQueueItem for ordering:
                #   * .status == Admitted items come before .status == Created items
                #   * Items with same status ordered by .creationTime
                entities.sort()
                for i, item in enumerate(entities):
                    if not item.waiting:
                        continue

                    if i < quotas[kind] or FLAGS.disable_quotas:
                        # TODO: per-account quotas

                        # Kubernetes is idempotent to multiple delivery because the jobs
                        # will have the same name and k8s will refuse to create the
                        # duplicate jobs, so k8s effectively turns at-least-once execution
                        # of the scheduling action into exactly-once execution.
                        try:
                            update = self.create_k8s_workflow(item.entity)
                        except Exception:
                            logging.exception("admission failed")
                            # TODO: Add enum entry for AdmissionFailed
                            update = {
                                "status": EntityStatus.error,
                                "reason": "AdmissionFailed",
                            }
                            if not FLAGS.debug_ignore_bad_messages:
                                raise
                        if update is not None:
                            # Failure here =>
                            #   * Next scheduling pass sees schedulable entity
                            #   * Double resource creation fails due to duplicate job name
                            #   => OK
                            self.produce_event(item.entity.id, update)
                            # Failure here =>
                            #   * Next scheduling pass sees schedulable entity
                            #   * Double resource creation fails due to duplicate job name
                            #   * Double event produced but Orchestrator will ignore it
                            #   => OK
                    elif item.entity.reason != EntityStatusReason.quota_limit:
                        # QuotaLimit
                        # The if-condition just reduces the number of redundant events
                        update = {
                            "status": EntityStatus.created,
                            "reason": EntityStatusReason.quota_limit,
                        }
                        self.produce_event(item.entity.id, update)
                        # Failure here =>
                        #   * Next scheduling pass sees blocked entity
                        #   * Double event produced but Orchestrator will ignore it
                        #   => OK

    def process_message(self, msg: kafka.Message):
        """Update the local RocksDB in response to an incoming Kafka message.

        The state of the entity in the message is always updated to keep the local
        snapshot in sync with the Kafka topic.

        The dependency graph is also updated in the following two cases:
          * A brand new entity in Created status (i.e., .reason is None)
          * An entity in a terminal status (finished or failed)

        No actions are taken here that modify the state of the system outside of
        the Orchestrator. Scheduling actions occur separately in
        ``maybe_admit_more_workflows()``, which runs periodically on a timer. The
        admission process may require significant computation if there are a lot
        of pending jobs, so executing it on every event would be excessive.
        """

        # To ensure fault tolerance, we need to make scheduling decisions based on
        # the current state, not on state transitions (similar to how the k8s
        # operator is implemented).
        #
        # Recording the state in the local DB is semantically similar to commiting
        # the consumer position in Kafka, i.e., it needs to happen *after* taking
        # any other actions so we have at-least-once execution of those actions.

        id = deserialize_id(msg.key())
        entity = deserialize_entity(msg.value())
        if id != entity.id:
            logging.error(
                f"message key {id} != entity.id {entity.id}; skipping message"
            )
            return
        logging.info(f"process_message(): {id}: {entity}")

        # Short-circuit for some duplicate messages that are easy to detect.
        # This doesn't catch all double message deliveries, because failure between
        # db.put() and consumer.commit() leaves db ahead of consumer.
        stored_entity = self.db.get_entity(entity.id)
        if stored_entity == entity:
            logging.debug(f"rejected duplicate message: {entity}")
            return

        # RocksDB batch write happens in a single transaction
        write_batch = LocalDBWriteBatch()

        # These are the two status events that might change the dependency graph
        if entity.status == EntityStatus.created and entity.reason is None:
            update = self.dependency_graph.add_created(self.db, entity)
            write_batch.put_dependency_graph(self.dependency_graph)
            if update:
                self.produce_event(entity.id, update)
        elif is_status_terminal(entity.status):
            if entity.status in [EntityStatus.deleted, EntityStatus.terminated]:
                # TODO: We could delete all k8s entities that are in terminal
                # states, but it's useful to keep them around for debugging.
                # Alternatively, we could pass the Terminated status through
                # to the operator, so it can delete child workflows but leave
                # the parent workflow in k8s for examination.
                try:
                    self.delete_k8s_workflow(entity)
                except kubernetes.client.exceptions.ApiException as ex:
                    # NotFound is OK because we might have a duplicate message
                    # or a user might delete the entity after the k8s resource
                    # has been GC'd.
                    if ex.status != 404:
                        raise
            changed_dependents: List[DyffEntityType] = (
                self.dependency_graph.on_workflow_termination(self.db, entity)
            )
            for e in changed_dependents:
                self.produce_event(e.id, {"status": e.status, "reason": e.reason})
                write_batch.put_entity(e.id, e)
            write_batch.put_dependency_graph(self.dependency_graph)

        # Store state change in local DB
        write_batch.put_entity(entity.id, entity)
        # DB write is last step so that we get at-least-once execution of the
        # dependency graph update.
        self.db.write_batch(write_batch)
        # Failure here =>
        #   * State msg received again
        #   * (Possible) Event msg produced again but orchestrator will ignore
        #   * Double put in DB but the value is the same
        #   => OK
        self.log_debug_db()

    def run(self, *, once: bool = False):
        """Run the Orchestrator loop forever.

        If ``once == True``, return after running the loop once, including one run
        of the scheduling step.
        """

        def datetime_now() -> datetime.datetime:
            return datetime.datetime.now(datetime.timezone.utc)

        def reset_partition_offsets_to_beginning(consumer, partitions):
            for partition in partitions:
                # Note: -2 is the Kafka special value meaning "from beginning"
                partition.offset = -2
            consumer.assign(partitions)

        scheduler_interval = datetime.timedelta(seconds=10)
        subscriptions = [self.workflows_state_topic]

        if FLAGS.from_beginning:
            self.consumer.subscribe(
                subscriptions, on_assign=reset_partition_offsets_to_beginning
            )
        else:
            self.consumer.subscribe(subscriptions)
        # This starts as None so that scheduling always runs on the first iteration,
        # otherwise the --once flag would be fairly useless
        then = None
        while True:
            # Kafka messages update the local DB state, but we only act on them
            # periodically
            msg = self.consumer.poll(timeout=1.0)
            if msg is not None:
                if msg.error():
                    if msg.error().code() == kafka.KafkaError._PARTITION_EOF:
                        logging.warning(
                            f"{msg.topic()}:{msg.partition()} EOF at offset {msg.offset()}"
                        )
                    else:
                        raise kafka.KafkaException(msg.error())
                else:
                    try:
                        # Want "at least once" delivery of state message
                        #   => "process" must happen before "commit"
                        self.process_message(msg)
                    except Exception:
                        logging.error(f"bad message: {msg.value()}")
                        if not FLAGS.debug_ignore_bad_messages:
                            raise
                    # Failure here =>
                    #   * DB update happens again
                    #   => OK (see process_message)
                    self.consumer.commit(asynchronous=True)

            # Periodically check if we can schedule more stuff
            now = datetime_now()
            if (then is None) or (now - then >= scheduler_interval):
                try:
                    self.maybe_admit_more_workflows()
                except pydantic.ValidationError:
                    logging.error(f"schema error in DB")
                    if not FLAGS.debug_ignore_bad_messages:
                        raise
                then = now

            if once:
                break


def main(_unused_argv):
    load_config()

    orchestrator = Orchestrator(
        local_db_path=FLAGS.local_db_path,
        workflows_events_topic=(
            FLAGS.workflows_events_topic or config.kafka.topics.workflows_events
        ),
        workflows_state_topic=(
            FLAGS.workflows_state_topic or config.kafka.topics.workflows_state
        ),
        kafka_bootstrap_servers=(
            FLAGS.kafka_bootstrap_servers or config.kafka.config.bootstrap_servers
        ),
        disable_kafka_producer=FLAGS.disable_kafka_producer,
        disable_kubernetes_actions=FLAGS.disable_kubernetes_actions,
    )
    try:
        orchestrator.run(once=FLAGS.once)
    finally:
        orchestrator.close()
