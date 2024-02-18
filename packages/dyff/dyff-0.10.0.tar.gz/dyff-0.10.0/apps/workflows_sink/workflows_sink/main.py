# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
import pymongo
import pymongo.write_concern
from absl import logging
from confluent_kafka import Consumer, KafkaError, KafkaException, Message

from dyff.api.backend.kafka.command import deserialize_id, deserialize_value
from dyff.api.typing import YAMLObject
from dyff.core.config import config
from dyff.schema import ids
from dyff.schema.platform import Entities, Resources


class WorkflowsSink:
    def __init__(self):
        connection_string = config.workflows_sink.mongodb.connection_string
        self._client = pymongo.MongoClient(connection_string.get_secret_value())
        self._workflows_db = self._client.get_database(
            config.workflows_sink.mongodb.database,
            write_concern=pymongo.write_concern.WriteConcern("majority", wtimeout=5000),
        )

    def process_message(self, msg: Message):
        logging.debug(f"{msg.key().decode()}: {msg.value().decode()}")

        def labels_object_to_array(obj: dict) -> list:
            # None value => Delete the label/annotation
            return [{"key": k, "value": v} for k, v in obj.items() if v is not None]

        def to_mongodb_entity(entity: YAMLObject) -> YAMLObject:
            d = dict(entity)
            d["_id"] = d.pop("id")
            # Transform the labels dict to a list of (k, v) pairs to avoid
            # problems with special characters in keys
            if "labels" in d:
                d["labels"] = labels_object_to_array(d["labels"])  # type: ignore
            # TODO: Do the same for annotations
            # if "annotations" in d:
            #     d["annotations"] = object_to_array(d["annotations"])
            return d

        key = deserialize_id(msg.key())
        entity = deserialize_value(msg.value())
        entity_id = entity.get("id")

        if entity_id is None:
            logging.error(f"entity.id is None; skipping message")
            return
        if key != entity_id:
            logging.error(f"entity.id {entity_id} != key {key}; skipping message")
            return
        if key == ids.null_id() or entity_id == ids.null_id():
            logging.debug(f"skipping null ID: {msg}")
            return

        try:
            entity_kind = entity["kind"]
            entity = to_mongodb_entity(entity)
            resource = Resources.for_kind(Entities(entity_kind))
        except KeyError:
            logging.exception(
                f"entity missing required field; skipping message; in:\n{msg}"
            )
            return
        except ValueError:
            logging.exception(
                f"unexpected unhandled kind; skipping message; {entity_kind} in:\n{msg}"
            )
            return

        logging.info(f"update: {entity_id}")
        self._workflows_db[resource].update_one(
            {"_id": entity_id}, {"$set": entity}, upsert=True
        )

    def on_commit(self, error, partitions):
        if error:
            logging.error(error)
        else:
            logging.debug(f"committed partition offsets: {partitions}")

    def run(self) -> None:
        consumer_config = {
            "bootstrap.servers": config.kafka.config.bootstrap_servers,
            "group.id": "dyff.system.mongodb.sink",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "on_commit": self.on_commit,
        }
        consumer = Consumer(consumer_config)

        try:
            consumer.subscribe([config.kafka.topics.workflows_state])
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logging.warning(
                            f"{msg.topic()}:{msg.partition()} EOF at offset {msg.offset()}"
                        )
                    else:
                        raise KafkaException(msg.error())
                else:
                    # consumer.commit() after processing => at-least-once processing
                    self.process_message(msg)
                    consumer.commit(asynchronous=True)
        finally:
            consumer.close()
