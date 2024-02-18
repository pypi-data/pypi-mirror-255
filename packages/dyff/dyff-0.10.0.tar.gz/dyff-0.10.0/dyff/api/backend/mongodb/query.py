# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from typing import Collection, Iterable, Optional

import pymongo

from dyff.core.config import config
from dyff.schema.platform import (
    Audit,
    Dataset,
    DataSource,
    Entities,
    Evaluation,
    InferenceService,
    InferenceSession,
    Labeled,
    Model,
    Report,
    Resources,
)
from dyff.schema.requests import (
    AuditQueryRequest,
    DatasetQueryRequest,
    EvaluationQueryRequest,
    InferenceServiceQueryRequest,
    InferenceSessionQueryRequest,
    ModelQueryRequest,
    ReportQueryRequest,
)

from ..base.query import QueryBackend, Whitelist


class MongoDBQueryBackend(QueryBackend):
    def __init__(self):
        connection_string = config.api.query.mongodb.connection_string
        self._client = pymongo.MongoClient(connection_string.get_secret_value())
        self._workflows_db = self._client.get_database(
            config.api.query.mongodb.database
        )

    def _convert_entity_response(self, entity: dict) -> dict:
        def array_to_object(xs: list[dict]) -> dict:
            return {x["key"]: x["value"] for x in xs}

        entity = dict(entity)
        entity["id"] = entity["_id"]
        entity["labels"] = array_to_object(entity.get("labels", []))
        # TODO:
        # entity["annotations"] = array_to_object(entity["annotations"])
        del entity["_id"]
        return entity

    def _get_entity(self, kind: Entities, id: str) -> Optional[dict]:
        collection_name = Resources.for_kind(kind)
        collection = self._workflows_db[collection_name]
        result = collection.find_one({"_id": id})
        if result:
            result = self._convert_entity_response(result)
        return result

    def _query_entities(
        self, kind: Entities, whitelist: Whitelist, query: dict
    ) -> Iterable[dict]:
        print(f"whitelist: {whitelist}")
        mongo_conjunction: list[dict] = []
        if ("*" not in whitelist.accounts) and ("*" not in whitelist.entities):
            # Query constraint requiring the result to be in the whitelist
            mongo_conjunction.append(
                {
                    "$or": [
                        {"account": {"$in": list(whitelist.accounts)}},
                        {"_id": {"$in": list(whitelist.entities)}},
                    ]
                }
            )

        for k, v in query.items():
            if v is None:
                continue
            if k == "id":
                k = "_id"

            if k == "labels":
                labels = json.loads(v)
                labeled = Labeled(labels=labels)  # validate
                for label_key, label_value in labeled.labels.items():
                    mongo_conjunction.append(
                        {k: {"$elemMatch": {"key": label_key, "value": label_value}}}
                    )
            # TODO:
            # elif k == "annotations":
            #     pass
            elif isinstance(v, list):
                mongo_conjunction.append({k: {"$in": list(v)}})
            else:
                mongo_conjunction.append({k: v})

        query = {"$and": mongo_conjunction} if mongo_conjunction else {}
        print(f"query: {query}")
        collection_name = Resources.for_kind(kind)
        collection = self._workflows_db[collection_name]
        results = collection.find(query)

        for result in results:
            yield self._convert_entity_response(result)

    def _rename_query_key(self, query_dict: dict, old_key: str, new_key: str) -> None:
        """If query_dict contains a value for old_key, pop the value and
        add it back at new_key.
        """
        unset = object()
        value = query_dict.pop(old_key, unset)
        if value is not unset:
            query_dict[new_key] = value

    def get_audit(self, id: str) -> Optional[Audit]:
        """Retrieve an Audit entity.

        Parameters:
          id: The unique key of the Audit.

        Returns:
          The Audit, or None if no Audit with the specified key exists.
        """
        result = self._get_entity(Entities.Audit, id)
        return Audit.parse_obj(result) if result else None

    def query_audits(
        self, whitelist: Whitelist, query: AuditQueryRequest
    ) -> Collection[Audit]:
        """Retrieve all Audit entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Audit entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """
        qdict = query.dict()
        results = self._query_entities(Entities.Audit, whitelist, qdict)
        return [Audit.parse_obj(result) for result in results]

    def get_data_source(self, id: str) -> Optional[DataSource]:
        """Retrieve a DataSource entity.

        Parameters:
          id: The unique key of the DataSource.

        Returns:
          The DataSource, or None if no DataSource with the specified key exists.
        """
        result = self._get_entity(Entities.DataSource, id)
        return DataSource.parse_obj(result) if result else None

    def query_data_sources(
        self, whitelist: Whitelist, **query
    ) -> Collection[DataSource]:
        """Retrieve all DataSource entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the DataSource entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """
        results = self._query_entities(Entities.DataSource, whitelist, query)
        return [DataSource.parse_obj(result) for result in results]

    def get_dataset(self, id: str) -> Optional[Dataset]:
        """Retrieve a Dataset entity.

        Parameters:
          id: The unique key of the Dataset.

        Returns:
          The Dataset, or None if no Dataset with the specified key exists.
        """
        result = self._get_entity(Entities.Dataset, id)
        return Dataset.parse_obj(result) if result else None

    def query_datasets(
        self, whitelist: Whitelist, query: DatasetQueryRequest
    ) -> Collection[Dataset]:
        """Retrieve all Dataset entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Dataset entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """
        qdict = query.dict()
        results = self._query_entities(Entities.Dataset, whitelist, qdict)
        return [Dataset.parse_obj(result) for result in results]

    def get_evaluation(self, id: str) -> Optional[Evaluation]:
        """Retrieve an Evaluation entity.

        Parameters:
          id: The unique key of the Evaluation.

        Returns:
          The Evaluation, or None if no Evaluation with the specified key exists.
        """
        result = self._get_entity(Entities.Evaluation, id)
        return Evaluation.parse_obj(result) if result else None

    def query_evaluations(
        self, whitelist: Whitelist, query: EvaluationQueryRequest
    ) -> Collection[Evaluation]:
        """Retrieve all Evaluation entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Evaluation entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """
        qdict = query.dict()
        self._rename_query_key(
            qdict, "inferenceService", "inferenceSession.inferenceService.id"
        )
        self._rename_query_key(
            qdict, "inferenceServiceName", "inferenceSession.inferenceService.name"
        )
        self._rename_query_key(
            qdict, "model", "inferenceSession.inferenceService.model.id"
        )
        self._rename_query_key(
            qdict, "modelName", "inferenceSession.inferenceService.model.name"
        )
        results = self._query_entities(Entities.Evaluation, whitelist, qdict)
        return [Evaluation.parse_obj(result) for result in results]

    def get_inference_service(self, id: str) -> Optional[InferenceService]:
        """Retrieve an InferenceService entity.

        Parameters:
          id: The unique key of the InferenceService.

        Returns:
          The InferenceService, or None if no InferenceService with the specified key exists.
        """
        result = self._get_entity(Entities.InferenceService, id)
        return InferenceService.parse_obj(result) if result else None

    def query_inference_services(
        self, whitelist: Whitelist, query: InferenceServiceQueryRequest
    ) -> Collection[InferenceService]:
        """Retrieve all InferenceService entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the InferenceService entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """
        qdict = query.dict()
        self._rename_query_key(qdict, "model", "model.id")
        self._rename_query_key(qdict, "modelName", "model.name")
        results = self._query_entities(Entities.InferenceService, whitelist, qdict)
        return [InferenceService.parse_obj(result) for result in results]

    def get_inference_session(self, id: str) -> Optional[InferenceSession]:
        """Retrieve an InferenceSession entity.

        Parameters:
          id: The unique key of the InferenceSession.

        Returns:
          The InferenceSession, or None if no InferenceSession with the specified key exists.
        """
        result = self._get_entity(Entities.InferenceSession, id)
        return InferenceSession.parse_obj(result) if result else None

    def query_inference_sessions(
        self, whitelist: Whitelist, query: InferenceSessionQueryRequest
    ) -> Collection[InferenceSession]:
        """Retrieve all InferenceSession entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the InferenceSession entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """
        qdict = query.dict()
        self._rename_query_key(qdict, "inferenceService", "inferenceService.id")
        self._rename_query_key(qdict, "inferenceServiceName", "inferenceService.name")
        self._rename_query_key(qdict, "model", "inferenceService.model.id")
        self._rename_query_key(qdict, "modelName", "inferenceService.model.name")
        results = self._query_entities(Entities.InferenceSession, whitelist, qdict)
        return [InferenceSession.parse_obj(result) for result in results]

    def get_model(self, id: str) -> Optional[Model]:
        """Retrieve a Model entity.

        Parameters:
          id: The unique key of the Model.

        Returns:
          The Model, or None if no Model with the specified key exists.
        """
        result = self._get_entity(Entities.Model, id)
        return Model.parse_obj(result) if result else None

    def query_models(
        self, whitelist: Whitelist, query: ModelQueryRequest
    ) -> Collection[Model]:
        """Retrieve all Model entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Model entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """
        qdict = query.dict()
        results = self._query_entities(Entities.Model, whitelist, qdict)
        return [Model.parse_obj(result) for result in results]

    def get_report(self, id: str) -> Optional[Report]:
        """Retrieve a Report entity.

        Parameters:
          id: The unique key of the Report.

        Returns:
          The Report, or None if no Report with the specified key exists.
        """
        result = self._get_entity(Entities.Report, id)
        return Report.parse_obj(result) if result else None

    def query_reports(
        self, whitelist: Whitelist, query: ReportQueryRequest
    ) -> Collection[Report]:
        """Retrieve all Report entities matching the query parameters.

        Parameters:
          whitelist: The set of accounts and entities that the caller has
            been granted access to.
          **query: Equality constraints on fields of the Report entity.
            The returned entities satisfy 'entity.field==value' for all items
            'field: value' in kwargs.
        """
        qdict = query.dict()
        results = self._query_entities(Entities.Report, whitelist, qdict)
        return [Report.parse_obj(result) for result in results]
