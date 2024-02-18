# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
from __future__ import annotations

import json
import pathlib
import sys
from io import BytesIO
from typing import Any, BinaryIO, Callable, Optional, TypeVar

import httpx
import pandas
import pyarrow.dataset
from azure.core.credentials import AccessToken, TokenCredential

# We bring this into our namespace so that people can catch it without being
# confused by having to import 'azure.core'
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from azure.core.pipeline.transport import HttpResponse
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict

from dyff.schema.adapters import Adapter, create_pipeline
from dyff.schema.dataset import arrow, binary
from dyff.schema.platform import (
    Artifact,
    Audit,
    DataSchema,
    Dataset,
    Digest,
    DyffEntity,
    Evaluation,
    InferenceInterface,
    InferenceService,
    InferenceSession,
    InferenceSessionAndToken,
    Label,
    Model,
    Report,
    Status,
    StorageSignedURL,
)
from dyff.schema.requests import (
    DatasetCreateRequest,
    EvaluationCreateRequest,
    InferenceServiceCreateRequest,
    InferenceSessionCreateRequest,
    LabelUpdateRequest,
    ModelCreateRequest,
    ReportCreateRequest,
)

from ._generated import DyffAPI as RawClient
from ._generated._serialization import Serializer
from ._generated.operations._operations import (
    AuditproceduresOperations as AuditproceduresOperationsGenerated,
)
from ._generated.operations._operations import (
    AuditsOperations as AuditsOperationsGenerated,
)
from ._generated.operations._operations import (
    DatasetsOperations as DatasetsOperationsGenerated,
)
from ._generated.operations._operations import (
    EvaluationsOperations as EvaluationsOperationsGenerated,
)
from ._generated.operations._operations import (
    InferenceservicesOperations as InferenceservicesOperationsGenerated,
)
from ._generated.operations._operations import (
    InferencesessionsOperations as InferencesessionsOperationsGenerated,
)
from ._generated.operations._operations import (
    ModelsOperations as ModelsOperationsGenerated,
)
from ._generated.operations._operations import (
    ReportsOperations as ReportsOperationsGenerated,
)

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import (
        MutableMapping,  # type: ignore  # pylint: disable=ungrouped-imports
    )
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, HttpResponse], T, dict[str, Any]], Any]
]


_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def _require_id(x: DyffEntity | str) -> str:
    if isinstance(x, str):
        return x
    elif x.id is not None:
        return x.id
    else:
        raise ValueError(".id attribute not set")


def _encode_labels(labels: Optional[dict[str, str]]) -> Optional[str]:
    """The Python client accepts 'annotations' and 'labels' as dicts, but
    they need to be json-encoded so that they can be forwarded as part of
    the HTTP query parameters.
    """
    if labels is None:
        return None
    # validate
    for k, v in labels.items():
        try:
            Label(key=k, value=v)
        except Exception as ex:
            raise HttpResponseError(
                f"label ({k}: {v}) has invalid format", status_code=400
            ) from ex
    return json.dumps(labels)


def build_audits_upload_request(
    audit_id: str, *, file: BinaryIO, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})

    # Note: Do not set the content type manually. Azure will figure out that
    # it's multipart/form-data and generate the '; boundary=...' part.
    content_type: Optional[str] = kwargs.pop(
        "content_type", _headers.pop("Content-Type", None)
    )
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/audits/{audit_id}/upload"
    path_format_arguments = {
        "audit_id": _SERIALIZER.url("audit_id", audit_id, "str"),
    }

    _url = _url.format(**path_format_arguments)

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header(
            "content_type", content_type, "str"
        )
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    # Note: The key is the name of the parameter in FastAPI
    # It's not obvious from the documentation of HttpRequest, but the file has
    # to be a file-like object. Even though HttpRequest will accept the file
    # data instead, this will not get encoded/decoded correctly for FastAPI
    # to work with it.
    # See: azure.core.utils._pipeline_transport_rest_shared._format_data_helper()
    # The error if you provide the data instead:
    # {'detail': [{'loc': ['body', 'file'], 'msg': "Expected UploadFile, received: <class 'str'>", 'type': 'value_error'}]}
    files = {"file": file}
    # Note: The annotated type of 'files' might not be accurate
    return HttpRequest(method="POST", url=_url, headers=_headers, files=files, **kwargs)  # type: ignore


class InferenceSessionClient:
    """A client used for making inference requests to a running
    :class:`~dyff.schema.platform.InferenceSession`.

    .. note::

      Do not instantiate this class. Create an instance using
      :meth:`inferencesessions.client() <dyff.client.client.InferencesessionsOperations>`
    """

    def __init__(
        self,
        *,
        session_id: str,
        token: str,
        dyff_api_endpoint: str,
        inference_endpoint: str,
        input_adapter: Optional[Adapter] = None,
        output_adapter: Optional[Adapter] = None,
    ):
        self._session_id = session_id
        self._token = token
        self._dyff_api_endpoint = dyff_api_endpoint

        self._inference_endpoint = inference_endpoint
        self._input_adapter = input_adapter
        self._output_adapter = output_adapter

        self._client = httpx.Client(timeout=httpx.Timeout(5, read=None))

    def infer(self, body: Any) -> Any:
        """Make an inference request.

        The input and output are arbitrary JSON objects. The required format
        depends on the endpoint and input/output adapters specified when
        creating the inference client.

        :param Any body: A JSON object containing the inference input.
        :returns: A JSON object containing the inference output.
        """
        url = httpx.URL(
            f"{self._dyff_api_endpoint}/inferencesessions"
            f"/{self._session_id}/infer/{self._inference_endpoint}"
        )
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self._token}",
        }

        def once(x):
            yield x

        body = once(body)
        if self._input_adapter is not None:
            body = self._input_adapter(body)
        for x in body:
            request = self._client.build_request("POST", url, headers=headers, json=x)
            response = self._client.send(request, stream=True)
            response.raise_for_status()
            response.read()
            json_response = once(response.json())
            if self._output_adapter is not None:
                json_response = self._output_adapter(json_response)
        return list(json_response)


class AuditsOperations:
    """Operations on :class:`~dyff.schema.platform.Audit` entities.

    .. note::

      Do not instantiate this class. Access it through the
      ``.audits`` attribute of :class:`~dyff.client.Client`.
    """

    def __init__(self, _raw_ops: AuditsOperationsGenerated):
        self._raw_ops = _raw_ops

    def get(self, audit_id: str) -> Audit:
        """Get an Audit by its key.

        :param audit_id: The audit id
        :type audit_id: str
        :return: The Audit with the given key.
        """
        return Audit.parse_obj(self._raw_ops.get(audit_id))

    def delete(self, audit_id: str) -> Status:
        """Mark an Audit for deletion.

        :param audit_id: The audit key
        :type audit_id: str
        :return: The resulting status of the entity
        :rtype: dyff.schema.platform.Status
        """
        return Status.parse_obj(self._raw_ops.delete(audit_id))

    def query(
        self,
        *,
        id: Optional[str] = None,
        account: Optional[str] = None,
        status: Optional[str] = None,
        reason: Optional[str] = None,
        labels: Optional[dict[str, str]] = None,
        name: Optional[str] = None,
    ) -> list[Audit]:
        """Get all Audits matching a query. The query is a set of equality
        constraints specified as key-value pairs.

        :keyword id:
        :paramtype id: str
        :keyword account:
        :paramtype account: str
        :keyword status:
        :paramtype status: str
        :keyword reason:
        :paramtype reason: str
        :keyword labels:
        :paramtype labels: dict[str, str]
        :keyword name: Default value is None.
        :paramtype name: str
        :return: list of ``Audit`` resources satisfying the query.
        :rtype: list[Audit]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return [
            Audit.parse_obj(obj)
            for obj in self._raw_ops.query(
                id=id,
                account=account,
                status=status,
                reason=reason,
                labels=_encode_labels(labels),
                name=name,
            )
        ]

    def label(self, audit_id: str, labels: dict[str, Optional[str]]) -> None:
        """Label the specified Audit with key-value pairs (stored in
        the ``.labels`` field of the resource).

        Providing ``None`` for the value deletes the label.

        See :class:`~dyff.schema.platform.Label` for a description of the
        constraints on label keys and values.

        :param audit_id: The ID of the Audit to label.
        :type audit_id: str
        :param labels: The label keys and values.
        :type labels: dict[str, Optional[str]]
        """
        if not labels:
            return
        labels = LabelUpdateRequest(labels=labels).dict()
        self._raw_ops.label(audit_id, labels)

    def upload(self, audit_id: str, file_path: str, **kwargs) -> None:
        """Upload an Audit report.

        Raises a 404 error if no entity exists with that key.

        :param audit_id: The Audit id.
        :type audit_id: str
        :param file_path: The path to the audit report data on the local file
            system. The report data must be packages as a ``.tar.gz`` archive.
        :type file_path: str
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        with open(file_path, "rb") as fin:
            request = build_audits_upload_request(
                audit_id=audit_id,
                file=fin,
                headers=_headers,
                params=_params,
            )
            request.url = self._raw_ops._client.format_url(request.url)

            _stream = False
            pipeline_response: PipelineResponse = (
                self._raw_ops._client._pipeline.run(  # pylint: disable=protected-access
                    request, stream=_stream, **kwargs
                )
            )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code, response=response, error_map=error_map
            )
            raise HttpResponseError(response=response)

        if response.status_code == 422:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None
            raise ValueError(f"Unprocessable entity: {deserialized}")


class AuditproceduresOperations:
    """Operations on :class:`~dyff.schema.platform.AuditProcedure` entities.

    .. note::

      Do not instantiate this class. Access it through the
      ``.auditprocedures`` attribute of :class:`~dyff.client.Client`.
    """

    def __init__(self, _raw_ops: AuditproceduresOperationsGenerated):
        self._raw_ops = _raw_ops

    def download(self, path: str) -> BytesIO:
        """Fetch the source code of an audit procedure.

        The data is returned as an in-memory ``.tar.gz`` archive.

        :param path: The relative path to the source code in the git repository.
        :type path: str
        :return: The audit procedure source code as an in-memory ``.tar.gz`` archive.
        """
        stream = self._raw_ops.download(path)
        blob = bytearray()
        for chunk in stream:
            blob.extend(chunk)  # type: ignore
        return BytesIO(blob)


class DatasetsOperations:
    """Operations on :class:`~dyff.schema.platform.Dataset` entities.

    .. note::

      Do not instantiate this class. Access it through the
      ``.datasets`` attribute of :class:`~dyff.client.Client`.
    """

    def __init__(self, _raw_ops: DatasetsOperationsGenerated):
        self._raw_ops = _raw_ops

    def get(self, dataset_id: str) -> Dataset:
        """Get a Dataset by its key.

        :param dataset_id: The dataset key
        :type dataset_id: str
        :return: The Dataset with the given key.
        """
        return Dataset.parse_obj(self._raw_ops.get(dataset_id))

    def delete(self, dataset_id: str) -> Status:
        """Mark a Dataset for deletion.

        :param dataset_id: The dataset key
        :type dataset_id: str
        :return: The resulting status of the entity
        :rtype: dyff.schema.platform.Status
        """
        return Status.parse_obj(self._raw_ops.delete(dataset_id))

    def query(
        self,
        *,
        id: Optional[str] = None,
        account: Optional[str] = None,
        status: Optional[str] = None,
        reason: Optional[str] = None,
        labels: Optional[dict[str, str]] = None,
        name: Optional[str] = None,
    ) -> list[Dataset]:
        """Get all Datasets matching a query. The query is a set of equality
        constraints specified as key-value pairs.

        :keyword id:
        :paramtype id: str
        :keyword account:
        :paramtype account: str
        :keyword status:
        :paramtype status: str
        :keyword reason:
        :paramtype reason: str
        :keyword labels:
        :paramtype labels: dict[str, str]
        :keyword name: Default value is None.
        :paramtype name: str
        :return: list of ``Dataset`` resources satisfying the query.
        :rtype: list[Dataset]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return [
            Dataset.parse_obj(obj)
            for obj in self._raw_ops.query(
                id=id,
                account=account,
                status=status,
                reason=reason,
                labels=_encode_labels(labels),
                name=name,
            )
        ]

    def label(self, dataset_id: str, labels: dict[str, Optional[str]]) -> None:
        """Label the specified Dataset with key-value pairs (stored in
        the ``.labels`` field of the resource).

        Providing ``None`` for the value deletes the label.

        See :class:`~dyff.schema.platform.Label` for a description of the
        constraints on label keys and values.

        :param dataset_id: The ID of the Dataset to label.
        :type dataset_id: str
        :param labels: The label keys and values.
        :type labels: dict[str, Optional[str]]
        """
        if not labels:
            return
        labels = LabelUpdateRequest(labels=labels).dict()
        self._raw_ops.label(dataset_id, labels)

    def strata(self, dataset: Dataset | str) -> pandas.DataFrame:
        """Fetch the strata of the dataset.

        :param dataset: The identifier of the dataset
        :type dataset: Dataset | str
        :return: The strata of the dataset
        """
        dataset = _require_id(dataset)
        stream = self._raw_ops.strata(dataset)
        blob = bytearray()
        for chunk in stream:
            blob.extend(chunk)  # type: ignore
        with BytesIO(blob) as fin:
            return pandas.read_parquet(fin)

    def data(self, dataset: Dataset | str) -> pyarrow.dataset.Scanner:
        """Fetch the raw data of the dataset.

        The data is returned as a read-once pyarrow Dataset.

        :param dataset: The identifier of the dataset
        :type dataset: Dataset | str
        :return: The strata of the dataset
        """
        dataset = _require_id(dataset)
        stream = self._raw_ops.data(dataset)
        buffer = bytearray()
        for chunk in stream:
            buffer.extend(chunk)  # type: ignore
        with pyarrow.ipc.open_stream(buffer) as reader:
            # Note: We should be able to pass 'reader' to 'from_batches()' directly
            # because it's already a batch generator, but if we do that then the
            # generator sometimes blocks program exit for some reason.
            def batch_generator():
                yield from reader

            return pyarrow.dataset.Scanner.from_batches(
                batch_generator(), schema=reader.schema
            )

    def create(self, dataset_request: DatasetCreateRequest) -> Dataset:
        """Create a Dataset.

        .. note::
            This operation may incur compute costs.

        :param dataset_request: The dataset request specification.
        :type dataset_request: DatasetCreateRequest
        :return: A full Dataset entity with .id and other properties set.
        """
        return Dataset.parse_obj(self._raw_ops.create(dataset_request.dict()))

    def create_arrow_dataset(
        self, dataset_directory: str, *, account: str, name: str
    ) -> Dataset:
        """Create a Dataset resource describing an existing Arrow dataset.

        Internally, constructs a ``DatasetCreateRequest`` using information
        obtained from the Arrow dataset, then calls ``create()`` with the
        constructed request.

        Typical usage::

            dataset = client.datasets.create_arrow_dataset(dataset_directory, ...)
            client.datasets.upload_arrow_dataset(dataset, dataset_directory)

        :param dataset_directory: The root directory of the Arrow dataset.
        :type dataset_directory: str
        :keyword account: The account that will own the Dataset resource.
        :type account: str
        :keyword name: The name of the Dataset resource.
        :type name: str
        :returns: The complete Dataset resource.
        :rtype: Dataset
        """
        dataset_path = pathlib.Path(dataset_directory)
        ds = arrow.open_dataset(str(dataset_path))
        file_paths = list(ds.files)
        artifact_paths = [
            str(pathlib.Path(file_path).relative_to(dataset_path))
            for file_path in file_paths
        ]
        artifacts = [
            Artifact(
                kind="parquet",
                path=artifact_path,
                digest=Digest(
                    md5=binary.encode(binary.file_digest("md5", file_path)),
                ),
            )
            for file_path, artifact_path in zip(file_paths, artifact_paths)
        ]
        schema = DataSchema(
            arrowSchema=arrow.encode_schema(ds.schema),
        )
        request = DatasetCreateRequest(
            account=account,
            name=name,
            artifacts=artifacts,
            schema=schema,
        )
        return self.create(request)

    def upload_arrow_dataset(self, dataset: Dataset, dataset_directory: str) -> None:
        """Uploads the data files in an existing Arrow dataset for which a
        Dataset resource has already been created.

        Typical usage::

            dataset = client.datasets.create_arrow_dataset(dataset_directory, ...)
            client.datasets.upload_arrow_dataset(dataset, dataset_directory)

        :param dataset: The Dataset resource for the Arrow dataset.
        :type dataset: Dataset
        :param dataset_directory: The root directory of the Arrow dataset.
        :type dataset_directory: str
        """
        if any(artifact.digest.md5 is None for artifact in dataset.artifacts):
            raise ValueError("artifact.digest.md5 must be set for all artifacts")
        for artifact in dataset.artifacts:
            assert artifact.digest.md5 is not None
            file_path = pathlib.Path(dataset_directory) / artifact.path
            put_url_json = self._raw_ops.upload(dataset.id, artifact.path)
            print(put_url_json)
            put_url = StorageSignedURL.parse_obj(put_url_json)
            if put_url.method != "PUT":
                raise ValueError(f"expected a PUT URL; got {put_url.method}")
            with open(file_path, "rb") as fin:
                headers = {
                    "content-md5": artifact.digest.md5,
                }
                headers.update(put_url.headers)
                response = httpx.put(put_url.url, data=fin, headers=headers)  # type: ignore
                print(response.request)
                print(response.request.headers)
                response.raise_for_status()
        self._raw_ops.finalize(dataset.id)


class EvaluationsOperations:
    """Operations on :class:`~dyff.schema.platform.Evaluation` entities.

    .. note::

      Do not instantiate this class. Access it through the
      ``.evaluations`` attribute of :class:`~dyff.client.Client`.
    """

    def __init__(self, _raw_ops: EvaluationsOperationsGenerated):
        self._raw_ops = _raw_ops

    def get(self, evaluation_id: str) -> Evaluation:
        """Get an Evaluation by its key.

        :param evaluation_id: The evaluation id
        :type evaluation_id: str
        :return: The Evaluation with the given key.
        """
        return Evaluation.parse_obj(self._raw_ops.get(evaluation_id))

    def delete(self, evaluation_id: str) -> Status:
        """Mark an Evaluation for deletion.

        :param evaluation_id: The evaluation key
        :type evaluation_id: str
        :return: The resulting status of the entity
        :rtype: dyff.schema.platform.Status
        """
        return Status.parse_obj(self._raw_ops.delete(evaluation_id))

    def query(
        self,
        *,
        id: Optional[str] = None,
        account: Optional[str] = None,
        status: Optional[str] = None,
        reason: Optional[str] = None,
        labels: Optional[dict[str, str]] = None,
        dataset: Optional[str] = None,
        inferenceService: Optional[str] = None,
        inferenceServiceName: Optional[str] = None,
        model: Optional[str] = None,
        modelName: Optional[str] = None,
    ) -> list[Evaluation]:
        """Get all Evaluations matching a query. The query is a set of equality
        constraints specified as key-value pairs.

        :keyword id:
        :paramtype id: str
        :keyword account:
        :paramtype account: str
        :keyword status:
        :paramtype status: str
        :keyword reason:
        :paramtype reason: str
        :keyword labels:
        :paramtype labels: dict[str, str]
        :keyword dataset:
        :paramtype dataset: str
        :keyword inferenceService:
        :paramtype inferenceService: str
        :keyword inferenceServiceName:
        :paramtype inferenceServiceName: str
        :keyword model:
        :paramtype model: str
        :keyword modelName:
        :paramtype modelName: str
        :return: list of ``Evaluation`` resources satisfying the query.
        :rtype: list[Evaluation]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return [
            Evaluation.parse_obj(obj)
            for obj in self._raw_ops.query(
                id=id,
                account=account,
                status=status,
                reason=reason,
                labels=_encode_labels(labels),
                dataset=dataset,
                inference_service=inferenceService,
                inference_service_name=inferenceServiceName,
                model=model,
                model_name=modelName,
            )
        ]

    def label(self, evaluation_id: str, labels: dict[str, Optional[str]]) -> None:
        """Label the specified Evaluation with key-value pairs (stored in
        the ``.labels`` field of the resource).

        Providing ``None`` for the value deletes the label.

        See :class:`~dyff.schema.platform.Label` for a description of the
        constraints on label keys and values.

        :param evaluation_id: The ID of the Evaluation to label.
        :type evaluation_id: str
        :param labels: The label keys and values.
        :type labels: dict[str, Optional[str]]
        """
        if not labels:
            return
        labels = LabelUpdateRequest(labels=labels).dict()
        self._raw_ops.label(evaluation_id, labels)

    def create(self, evaluation_request: EvaluationCreateRequest) -> Evaluation:
        """Create an Evaluation.

        .. note::
            This operation will incur compute costs.

        :param evaluation_request: The evaluation request specification.
        :type evaluation_request: EvaluationCreateRequest
        :return: A full Evaluation entity with .id and other properties set.
        """
        return Evaluation.parse_obj(self._raw_ops.create(evaluation_request.dict()))


class InferenceservicesOperations:
    """Operations on :class:`~dyff.schema.platform.InferenceService` entities.

    .. note::

      Do not instantiate this class. Access it through the
      ``.inferenceservices`` attribute of :class:`~dyff.client.Client`.
    """

    def __init__(self, _raw_ops: InferenceservicesOperationsGenerated):
        self._raw_ops = _raw_ops

    def get(self, service_id: str) -> InferenceService:
        """Get an InferenceService by its key.

        :param service_id: The inference service id
        :type service_id: str
        :return: The InferenceService with the given key.
        """
        return InferenceService.parse_obj(self._raw_ops.get(service_id))

    def delete(self, service_id: str) -> Status:
        """Mark an InferenceService for deletion.

        :param service_id: The inference service key
        :type service_id: str
        :return: The resulting status of the entity
        :rtype: dyff.schema.platform.Status
        """
        return Status.parse_obj(self._raw_ops.delete(service_id))

    def query(
        self,
        *,
        id: Optional[str] = None,
        account: Optional[str] = None,
        status: Optional[str] = None,
        reason: Optional[str] = None,
        labels: Optional[dict[str, str]] = None,
        name: Optional[str] = None,
        model: Optional[str] = None,
        modelName: Optional[str] = None,
    ) -> list[InferenceService]:
        """Get all InferenceServices matching a query. The query is a set of equality
        constraints specified as key-value pairs.

        :keyword id:
        :paramtype id: str
        :keyword account:
        :paramtype account: str
        :keyword status:
        :paramtype status: str
        :keyword reason:
        :paramtype reason: str
        :keyword labels:
        :paramtype labels: dict[str, str]
        :keyword name:
        :paramtype name: str
        :keyword model:
        :paramtype model: str
        :keyword modelName:
        :paramtype modelName: str
        :return: list of ``InferenceService`` resources satisfying the query.
        :rtype: list[InferenceService]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return [
            InferenceService.parse_obj(obj)
            for obj in self._raw_ops.query(
                id=id,
                account=account,
                status=status,
                reason=reason,
                labels=_encode_labels(labels),
                name=name,
                model=model,
                model_name=modelName,
            )
        ]

    def label(self, service_id: str, labels: dict[str, Optional[str]]) -> None:
        """Label the specified InferenceService with key-value pairs (stored in
        the ``.labels`` field of the resource).

        Providing ``None`` for the value deletes the label.

        See :class:`~dyff.schema.platform.Label` for a description of the
        constraints on label keys and values.

        :param service_id: The ID of the InferenceService to label.
        :type service_id: str
        :param labels: The label keys and values.
        :type labels: dict[str, Optional[str]]
        """
        if not labels:
            return
        labels = LabelUpdateRequest(labels=labels).dict()
        self._raw_ops.label(service_id, labels)

    def create(
        self, inference_service_request: InferenceServiceCreateRequest
    ) -> InferenceService:
        """Create an InferenceService.

        .. note::
            This operation may incur compute costs.

        :param inference_service_request: The inference service request specification.
        :type inference_service_request: InferenceServiceCreateRequest
        :return: A full InferenceService entity with .id and other properties set.
        """
        return InferenceService.parse_obj(
            self._raw_ops.create(inference_service_request.dict())
        )


class InferencesessionsOperations:
    """Operations on :class:`~dyff.schema.platform.Inferencesession` entities.

    .. note::

      Do not instantiate this class. Access it through the
      ``.inferencesessions`` attribute of :class:`~dyff.client.Client`.
    """

    def __init__(self, _raw_ops: InferencesessionsOperationsGenerated):
        self._raw_ops = _raw_ops

    def get(self, session_id: str) -> InferenceSession:
        """Get an InferenceSession by its key.

        :param session_id: The inference session id
        :type session_id: str
        :return: The InferenceSession with the given key.
        """
        return InferenceSession.parse_obj(self._raw_ops.get(session_id))

    def delete(self, session_id: str) -> Status:
        """Mark an InferenceSession for deletion.

        :param session_id: The inference session key
        :type session_id: str
        :return: The resulting status of the entity
        :rtype: dyff.schema.platform.Status
        """
        return Status.parse_obj(self._raw_ops.delete(session_id))

    def query(
        self,
        *,
        id: Optional[str] = None,
        account: Optional[str] = None,
        status: Optional[str] = None,
        reason: Optional[str] = None,
        labels: Optional[dict[str, str]] = None,
        name: Optional[str] = None,
        inferenceService: Optional[str] = None,
        inferenceServiceName: Optional[str] = None,
        model: Optional[str] = None,
        modelName: Optional[str] = None,
    ) -> list[InferenceSession]:
        """Get all InferenceSessions matching a query. The query is a set of equality
        constraints specified as key-value pairs.

        :keyword id:
        :paramtype id: str
        :keyword account:
        :paramtype account: str
        :keyword status:
        :paramtype status: str
        :keyword reason:
        :paramtype reason: str
        :keyword labels:
        :paramtype labels: dict[str, str]
        :keyword name:
        :paramtype name: str
        :keyword model:
        :paramtype model: str
        :keyword modelName:
        :paramtype modelName: str
        :return: list of ``InferenceSession`` resources satisfying the query.
        :rtype: list[InferenceSession]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return [
            InferenceSession.parse_obj(obj)
            for obj in self._raw_ops.query(
                id=id,
                account=account,
                status=status,
                reason=reason,
                labels=_encode_labels(labels),
                name=name,
                inference_service=inferenceService,
                inference_service_name=inferenceServiceName,
                model=model,
                model_name=modelName,
            )
        ]

    def label(self, session_id: str, labels: dict[str, Optional[str]]) -> None:
        """Label the specified InferenceSession with key-value pairs (stored in
        the ``.labels`` field of the resource).

        Providing ``None`` for the value deletes the label.

        See :class:`~dyff.schema.platform.Label` for a description of the
        constraints on label keys and values.

        :param session_id: The ID of the InferenceSession to label.
        :type session_id: str
        :param labels: The label keys and values.
        :type labels: dict[str, Optional[str]]
        """
        if not labels:
            return
        labels = LabelUpdateRequest(labels=labels).dict()
        self._raw_ops.label(session_id, labels)

    def create(
        self, inference_session_request: InferenceSessionCreateRequest
    ) -> InferenceSessionAndToken:
        """Create an InferenceSession.

        .. note::
            This operation will incur compute costs.

        :param account_id: The account that will own the evaluation.
        :type account_id: str
        :param inference_session_request: The inference service request specification.
        :type inference_session_request: InferenceSessionCreateRequest
        :return: A full InferenceSession entity with .id and other properties set.
        """
        return InferenceSessionAndToken.parse_obj(
            self._raw_ops.create(inference_session_request.dict())
        )

    def client(
        self,
        session_id: str,
        token: str,
        *,
        interface: Optional[InferenceInterface] = None,
        endpoint: Optional[str] = None,
        input_adapter: Optional[Adapter] = None,
        output_adapter: Optional[Adapter] = None,
    ) -> InferenceSessionClient:
        """Create an InferenceSessionClient that interacts with the given
        inference session. The token should be one returned either from
        ``Client.inferencesessions.create()`` or from
        ``Client.inferencesessions.token(session_id)``.

        The inference endpoint in the session must also be specified, either
        directly through the ``endpoint`` argument or by specifying an
        ``interface``. Specifying ``interface`` will also use the input and
        output adapters from the interface. You can also specify these
        separately in the ``input_adapter`` and ``output_adapter``. The
        non-``interface`` arguments override the corresponding values in
        ``interface`` if both are specified.

        :param session_id: The inference session to connect to
        :type session_id: str
        :param token: An access token with permission to run inference against
            the session.
        :type token: str
        :param interface: The interface to the session. Either ``interface``
            or ``endpoint`` must be specified.
        :type interface: Optional[InferenceInterface]
        :param endpoint: The inference endpoint in the session to call. Either
            ``endpoint`` or ``interface`` must be specified.
        :type endpoint: str
        :param input_adapter: Optional input adapter, applied to the input
            before sending it to the session. Will override the input adapter
            from ``interface`` if both are specified.
        :type input_adapter: Optional[Adapter]
        :param output_adapter: Optional output adapter, applied to the output
            of the session before returning to the client. Will override the
            output adapter from ``interface`` if both are specified.
        :type output_adapter: Optional[Adapter]
        :return: An ``InferenceSessionClient`` that makes inference calls to
            the specified session.
        """
        if interface is not None:
            endpoint = endpoint or interface.endpoint
            if input_adapter is None:
                if interface.inputPipeline is not None:
                    input_adapter = create_pipeline(interface.inputPipeline)
            if output_adapter is None:
                if interface.outputPipeline is not None:
                    output_adapter = create_pipeline(interface.outputPipeline)
        if endpoint is None:
            raise ValueError("either 'endpoint' or 'interface' is required")
        return InferenceSessionClient(
            session_id=session_id,
            token=token,
            dyff_api_endpoint=self._raw_ops._client._base_url,
            inference_endpoint=endpoint,
            input_adapter=input_adapter,
            output_adapter=output_adapter,
        )

    def ready(self, session_id: str) -> bool:
        """Return True if the session is ready to receive inference input.

        The readiness probe is expected to fail with status codes 404 or 503,
        as these will occur at times during normal session start-up. The
        ``ready()`` method returns False in these cases. Any other status
        codes will raise an ``HttpResponseError``.

        :param str session_id: The ID of the session.
        :raises HttpResponseError:
        """
        try:
            self._raw_ops.ready(session_id)
        except HttpResponseError as ex:
            if ex.status_code in [404, 503]:
                return False
            else:
                raise
        return True

    def terminate(self, session_id: str) -> Status:
        """Terminate a session.

        :param session_id: The inference session key
        :type session_id: str
        :return: The resulting status of the entity
        :rtype: dyff.schema.platform.Status
        :raises HttpResponseError:
        """
        return Status.parse_obj(self._raw_ops.terminate(session_id))

    def token(self, session_id: str) -> str:
        """Create a session token.

        The session token is a short-lived token that allows the bearer to
        make inferences with the session (via an ``InferenceSessionClient``)
        and to call ``ready()``, ``get()``, and ``terminate()`` on the session.

        :param str session_id: The ID of the session.
        :raises HttpResponseError:
        """
        return str(self._raw_ops.token(session_id))


class ModelsOperations:
    """Operations on :class:`~dyff.schema.platform.Model` entities.

    .. note::

      Do not instantiate this class. Access it through the
      ``.models`` attribute of :class:`~dyff.client.Client`.
    """

    def __init__(self, _raw_ops: ModelsOperationsGenerated):
        self._raw_ops = _raw_ops

    def get(self, model_id: str) -> Model:
        """Get a Model by its key.

        :param model_id: The inference service id
        :type model_id: str
        :return: The Model with the given key.
        """
        return Model.parse_obj(self._raw_ops.get(model_id))

    def delete(self, model_id: str) -> Status:
        """Mark a Model for deletion.

        :param model_id: The model key
        :type model_id: str
        :return: The resulting status of the entity
        :rtype: dyff.schema.platform.Status
        """
        return Status.parse_obj(self._raw_ops.delete(model_id))

    def query(
        self,
        *,
        id: Optional[str] = None,
        account: Optional[str] = None,
        status: Optional[str] = None,
        reason: Optional[str] = None,
        labels: Optional[dict[str, str]] = None,
        name: Optional[str] = None,
    ) -> list[Model]:
        """Get all Models matching a query. The query is a set of equality
        constraints specified as key-value pairs.

        :keyword id:
        :paramtype id: str
        :keyword account:
        :paramtype account: str
        :keyword status:
        :paramtype status: str
        :keyword reason:
        :paramtype reason: str
        :keyword labels:
        :paramtype labels: dict[str, str]
        :keyword name:
        :paramtype name: str
        :return: list of ``Model`` resources satisfying the query.
        :rtype: list[Model]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return [
            Model.parse_obj(obj)
            for obj in self._raw_ops.query(
                id=id,
                account=account,
                status=status,
                reason=reason,
                labels=_encode_labels(labels),
                name=name,
            )
        ]

    def label(self, model_id: str, labels: dict[str, Optional[str]]) -> None:
        """Label the specified Model with key-value pairs (stored in
        the ``.labels`` field of the resource).

        Providing ``None`` for the value deletes the label.

        See :class:`~dyff.schema.platform.Label` for a description of the
        constraints on label keys and values.

        :param model_id: The ID of the Model to label.
        :type model_id: str
        :param labels: The label keys and values.
        :type labels: dict[str, Optional[str]]
        """
        if not labels:
            return
        labels = LabelUpdateRequest(labels=labels).dict()
        self._raw_ops.label(model_id, labels)

    def create(self, model_request: ModelCreateRequest) -> Model:
        """Create a Model.

        .. note::
            This operation will incur compute costs.

        :param model_request: The model specification.
        :type model: Model
        :return: A full Model entity with .id and other properties set.
        """
        return Model.parse_obj(self._raw_ops.create(model_request.dict()))


class ReportsOperations:
    """Operations on :class:`~dyff.schema.platform.Report` entities.

    .. note::

      Do not instantiate this class. Access it through the
      ``.reports`` attribute of :class:`~dyff.client.Client`.
    """

    def __init__(self, _raw_ops: ReportsOperationsGenerated):
        self._raw_ops = _raw_ops

    def get(self, report_id: str) -> Report:
        """Get a Report by its key.

        :param report_id: The report id
        :type report_id: str
        :return: The Report with the given key.
        """
        return Report.parse_obj(self._raw_ops.get(report_id))

    def delete(self, report_id: str) -> Status:
        """Mark a Report for deletion.

        :param report_id: The report key
        :type report_id: str
        :return: The resulting status of the entity
        :rtype: dyff.schema.platform.Status
        """
        return Status.parse_obj(self._raw_ops.delete(report_id))

    def query(
        self,
        *,
        id: Optional[str] = None,
        account: Optional[str] = None,
        status: Optional[str] = None,
        reason: Optional[str] = None,
        labels: Optional[dict[str, str]] = None,
        report: Optional[str] = None,
        dataset: Optional[str] = None,
        evaluation: Optional[str] = None,
        inferenceService: Optional[str] = None,
        model: Optional[str] = None,
    ) -> list[Report]:
        """Get all Reports matching a query. The query is a set of equality
        constraints specified as key-value pairs.

        :keyword id:
        :paramtype id: str
        :keyword account:
        :paramtype account: str
        :keyword status:
        :paramtype status: str
        :keyword reason:
        :paramtype reason: str
        :keyword labels:
        :paramtype labels: dict[str, str]
        :keyword report:
        :paramtype report: str
        :keyword dataset:
        :paramtype dataset: str
        :keyword evaluation:
        :paramtype evaluation: str
        :keyword inferenceService:
        :paramtype inferenceService: str
        :keyword model:
        :paramtype model: str
        :return: list of ``Report`` resources satisfying the query.
        :rtype: list[Report]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return [
            Report.parse_obj(obj)
            for obj in self._raw_ops.query(
                id=id,
                account=account,
                status=status,
                reason=reason,
                labels=_encode_labels(labels),
                report=report,
                dataset=dataset,
                evaluation=evaluation,
                inference_service=inferenceService,
                model=model,
            )
        ]

    def label(self, report_id: str, labels: dict[str, Optional[str]]) -> None:
        """Label the specified Report with key-value pairs (stored in
        the ``.labels`` field of the resource).

        Providing ``None`` for the value deletes the label.

        See :class:`~dyff.schema.platform.Label` for a description of the
        constraints on label keys and values.

        :param report_id: The ID of the Report to label.
        :type report_id: str
        :param labels: The label keys and values.
        :type labels: dict[str, Optional[str]]
        """
        if not labels:
            return
        labels = LabelUpdateRequest(labels=labels).dict()
        self._raw_ops.label(report_id, labels)

    def create(self, report_request: ReportCreateRequest) -> Report:
        """Create a Report.

        .. note::
            This operation will incur compute costs.

        :param report_request: The report specification.
        :type report: ReportCreateRequest
        :return: A full Report entity with .id and other properties set.
        """
        return Report.parse_obj(self._raw_ops.create(report_request.dict()))

    def data(self, report: Report | str) -> pandas.DataFrame:
        """Fetch the output data of the report.

        :param report: The identifier of the report
        :type report: Report | str
        :return: The output data of the report
        """
        report = _require_id(report)
        stream = self._raw_ops.data(report)
        blob = bytearray()
        for chunk in stream:
            blob.extend(chunk)  # type: ignore
        with BytesIO(blob) as fin:
            return pandas.read_parquet(fin)


class _APIKeyCredential(TokenCredential):
    def __init__(self, *, api_key: str):
        self.api_key = api_key

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AccessToken:
        return AccessToken(self.api_key, -1)


class Client:
    """The Python client for the Dyff Platform API.

    API operations are grouped by the resource type that they manipulate. For
    example, all operations on ``Evaluation`` resources are accessed like
    ``client.evaluations.create()``.

    The Python API functions may have somewhat different behavior from the
    corresponding API endpoints, and the Python client also adds several
    higher-level API functions that are implemented with multiple endpoint
    calls.
    """

    def __init__(
        self,
        *,
        api_key: str,
        endpoint: Optional[str] = None,
        verify_ssl_certificates: bool = True,
    ):
        """
        :param str api_key: An API token to use for authentication.
        :param str endpoint: The URL where the Dyff Platform API is hosted.
            Defaults to the UL DSRI-hosted Dyff instance.
        :param bool verify_ssl_certificates: You can disable certificate
            verification for testing; you should do this only if you have
            also changed ``endpoint`` to point to a trusted local server.
        """

        if endpoint is None:
            endpoint = "https://apis.alignmentlabs.ai/dyff/v0"
        credential = _APIKeyCredential(api_key=api_key)
        authentication_policy = BearerTokenCredentialPolicy(credential)
        self._raw = RawClient(
            endpoint=endpoint,
            credential=credential,
            authentication_policy=authentication_policy,
        )

        # We want the ability to disable SSL certificate verification for testing
        # on localhost. It should be possible to do this via the Configuration object:
        # e.g., config.<some_field> = azure.core.configuration.ConnectionConfiguration(connection_verify=False)
        #
        # The docs state that the ConnectionConfiguration class is "Found in the Configuration object."
        # https://learn.microsoft.com/en-us/python/api/azure-core/azure.core.configuration.connectionconfiguration?view=azure-python
        #
        # But at no point do they say what the name of the field should be! The
        # docs for azure.core.configuration.Configuration don't mention any
        # connection configuration. The field is called 'connection_config' in the
        # _transport member of _pipeline, but _transport will not pick up the
        # altered ConnectionConfiguration if it is set on 'config.connection_config'
        #
        # Example:
        # client._config.connection_config = ConnectionConfiguration(connection_verify=False)
        # [in Client:]
        # >>> print(self._config.connection_config.verify)
        # False
        # >> print(self._pipeline._transport.connection_config.verify)
        # True
        self._raw._client._pipeline._transport.connection_config.verify = (  # type: ignore
            verify_ssl_certificates
        )

        self._audits = AuditsOperations(self._raw.audits)
        self._auditprocedures = AuditproceduresOperations(self._raw.auditprocedures)
        self._datasets = DatasetsOperations(self._raw.datasets)
        self._evaluations = EvaluationsOperations(self._raw.evaluations)
        self._inferenceservices = InferenceservicesOperations(
            self._raw.inferenceservices
        )
        self._inferencesessions = InferencesessionsOperations(
            self._raw.inferencesessions
        )
        self._models = ModelsOperations(self._raw.models)
        self._reports = ReportsOperations(self._raw.reports)

    @property
    def raw(self) -> RawClient:
        """The "raw" API client, which can be used to send JSON requests directly."""
        return self._raw

    @property
    def audits(self) -> AuditsOperations:
        """Operations on :class:`~dyff.schema.platform.Audit` entities."""
        return self._audits

    @property
    def auditprocedures(self) -> AuditproceduresOperations:
        """Operations on :class:`~dyff.schema.platform.AuditProcedure` entities."""
        return self._auditprocedures

    @property
    def datasets(self) -> DatasetsOperations:
        """Operations on :class:`~dyff.schema.platform.Dataset` entities."""
        return self._datasets

    @property
    def evaluations(self) -> EvaluationsOperations:
        """Operations on :class:`~dyff.schema.platform.Evaluation` entities."""
        return self._evaluations

    @property
    def inferenceservices(self) -> InferenceservicesOperations:
        """Operations on :class:`~dyff.schema.platform.InferenceService` entities."""
        return self._inferenceservices

    @property
    def inferencesessions(self) -> InferencesessionsOperations:
        """Operations on :class:`~dyff.schema.platform.InferenceSession` entities."""
        return self._inferencesessions

    @property
    def models(self) -> ModelsOperations:
        """Operations on :class:`~dyff.schema.platform.Model` entities."""
        return self._models

    @property
    def reports(self) -> ReportsOperations:
        """Operations on :class:`~dyff.schema.platform.Report` entities."""
        return self._reports


__all__ = [
    "Client",
    "InferenceSessionClient",
    "RawClient",
    "HttpResponseError",
]
