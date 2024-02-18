# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
import json
from typing import Optional, TypeVar

import pydantic
from confluent_kafka import Producer

from dyff.api import timestamp
from dyff.api.typing import YAMLObject
from dyff.core.config import config
from dyff.schema import ids
from dyff.schema.platform import (
    Audit,
    Dataset,
    DataSource,
    DyffEntity,
    DyffEntityType,
    EntityStatus,
    EntityStatusReason,
    Evaluation,
    InferenceService,
    InferenceSession,
    Labeled,
    Model,
    Report,
)

from ..base.command import CommandBackend


def serialize_id(id: str) -> bytes:
    return id.encode("utf-8")


def serialize_value(value: YAMLObject) -> bytes:
    return json.dumps(value).encode("utf-8")


def serialize_entity(entity: DyffEntity) -> bytes:
    return entity.json().encode("utf-8")


def deserialize_id(id: bytes) -> str:
    return id.decode("utf-8")


def deserialize_value(value: bytes) -> YAMLObject:
    return json.loads(value.decode("utf-8"))


def deserialize_entity(entity: bytes) -> DyffEntityType:
    s = entity.decode("utf-8")
    # DyffEntityType is a pydantic "discriminated union", so pydantic infers
    # the type from the '.kind' field
    return pydantic.parse_raw_as(DyffEntityType, s)  # type: ignore


EntityT = TypeVar("EntityT", bound=DyffEntity)


class KafkaCommandBackend(CommandBackend):
    def __init__(self):
        self.events_topic = config.kafka.topics.workflows_events
        producer_config = config.kafka.config.get_producer_config()
        # FIXME: This should be the global default. It's supposed to be the
        # default in Kafka > 3.0, but the docs of librdkafka suggest that
        # its default is still False.
        # See: https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md
        producer_config["enable.idempotence"] = True
        # FIXME: See comment in alignmentlabs.dyff.web.server
        # Can't get real logging to work when running in uvicorn
        print(
            f"Creating KafkaCommandBackend with config:\n{json.dumps(producer_config, indent=2)}",
            flush=True,
        )
        # logging.info(f"Creating KafkaCommandBackend with config:\n{json.dumps(producer_config, indent=2)}")
        self._kafka_producer = Producer(producer_config)

    def _copy_and_add_system_fields(self, entity: EntityT) -> EntityT:
        entity = entity.copy()
        entity.creationTime = timestamp.now()
        entity.status = EntityStatus.created
        entity.id = ids.generate_entity_id()
        return entity

    def _produce_create_event(self, entity: EntityT) -> EntityT:
        entity = self._copy_and_add_system_fields(entity)
        assert entity.id is not None
        self._kafka_producer.produce(
            topic=self.events_topic,
            value=serialize_entity(entity),
            key=serialize_id(entity.id),
        )
        return entity

    def _produce_terminate_event(self, id: str) -> None:
        update = {
            "status": EntityStatus.terminated,
            "reason": EntityStatusReason.terminate_command,
        }
        self._kafka_producer.produce(
            topic=self.events_topic,
            value=serialize_value(update),
            key=serialize_id(id),
        )

    def update_status(
        self, id: str, *, status: str, reason: Optional[str] = None
    ) -> None:
        """Update the status of an entity.

        Parameters:
          id: The entity .id
          status: New .status value
          reason: New .reason value
        """
        update = {
            "status": status,
            "reason": reason,
        }
        self._kafka_producer.produce(
            topic=self.events_topic,
            value=serialize_value(update),
            key=serialize_id(id),
        )

    def update_labels(self, id: str, labels: Labeled) -> None:
        """Updated the labels of a labeled entity.

        :param id: The ID of the entity to update.
        :type id: str
        :param labels: The labels to update.
        :type labels: Labeled
        """
        update = labels.dict()
        self._kafka_producer.produce(
            topic=self.events_topic, value=serialize_value(update), key=serialize_id(id)
        )

    def create_audit(self, spec: Audit) -> Audit:
        """Create a new Audit entity in the system.

        Parameters:
          spec: Specification of the Audit. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """
        return self._produce_create_event(spec)

    def create_data_source(self, spec: DataSource) -> DataSource:
        """Create a new DataSource entity in the system.

        Parameters:
          spec: Specification of the DataSource. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """
        return self._produce_create_event(spec)

    def create_dataset(self, spec: Dataset) -> Dataset:
        """Create a new Dataset entity in the system.

        Parameters:
          spec: Specification of the Dataset. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """
        return self._produce_create_event(spec)

    def create_evaluation(self, spec: Evaluation) -> Evaluation:
        """Create a new Evaluation entity in the system.

        Parameters:
          spec: Specification of the Evaluation. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """
        return self._produce_create_event(spec)

    def create_inference_service(self, spec: InferenceService) -> InferenceService:
        """Create a new InferenceService entity in the system.

        Parameters:
          spec: Specification of the InferenceService. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """
        return self._produce_create_event(spec)

    def create_inference_session(self, spec: InferenceSession) -> InferenceSession:
        """Create a new InferenceSession entity in the system.

        Parameters:
          spec: Specification of the InferenceSession. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """
        return self._produce_create_event(spec)

    def create_model(self, spec: Model) -> Model:
        """Create a new Model entity in the system.

        Parameters:
          spec: Specification of the Model. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """
        return self._produce_create_event(spec)

    def create_report(self, spec: Report) -> Report:
        """Create a new Report entity in the system.

        Parameters:
          spec: Specification of the Report. The system fields of the spec
            such as ``.id`` must be **unset**.

        Returns:
          A copy of ``spec`` with all system fields set.
        """
        return self._produce_create_event(spec)
