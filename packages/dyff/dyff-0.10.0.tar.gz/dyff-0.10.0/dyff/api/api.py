# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

"""FastAPI definition of the alignmentlabs.dyff Web API.

Naming conventions
------------------

Endpoint functions must be named like ``category_operation()``, e.g.,
``reports_create()``, and the name must be **globally unique**, even if
the functions are defined in different namespaces. We rely on this format
in two places:

#. The autorest code generator exposes the functions like
``DyffAPI.reports.create()``, where the names are determined by splitting
the endpoint function name on underscores. To facilitate this, we strip all of
the unique-ifying information from the OpenAPI ``operationId`` fields generated
by FastAPI, leaving only the function name (that's why it must be unique).
#. API keys grant access to specific resources and functions on those
resources. We determine which resource and function is being requested
by, again, splitting the endpoint function name on underscores.
"""

# mypy: disable-error-code="import-untyped"

# Note: This breaks fastapi, with a NameError while resolving forward refs.
# The underlying issue is that the Endpoint class has a forward reference
# in one of its functions, and Endpoint is used in a fastapi Depends() context.
# from __future__ import annotations

import base64
import datetime
import functools
import io
import json
import tarfile
from pathlib import Path
from typing import IO, Container, Iterable, NamedTuple, Optional, TypeVar

import fastapi
import fastapi.security
import gitlab
import httpx
import pyarrow
import smart_open
import starlette.background
from fastapi.security.utils import get_authorization_scheme_param

from dyff.api import storage, tokens
from dyff.api.backend.base.auth import AuthBackend
from dyff.api.backend.base.command import CommandBackend
from dyff.api.backend.base.query import QueryBackend, Whitelist
from dyff.api.sanitize import sanitize_relative_file_path
from dyff.core import dynamic_import
from dyff.core.config import config
from dyff.schema import ids
from dyff.schema.dataset import arrow
from dyff.schema.platform import (
    AccessGrant,
    APIFunctions,
    APIKey,
    Audit,
    Dataset,
    DatasetStatus,
    DyffEntity,
    DyffModelWithID,
    Entities,
    EntityStatus,
    EntityStatusReason,
    Evaluation,
    InferenceService,
    InferenceSession,
    InferenceSessionAndToken,
    Model,
    Report,
    Resources,
    Status,
    StorageSignedURL,
    is_status_success,
    is_status_terminal,
)
from dyff.schema.requests import (
    AuditQueryRequest,
    DatasetCreateRequest,
    DatasetQueryRequest,
    EvaluationCreateRequest,
    EvaluationQueryRequest,
    InferenceServiceCreateRequest,
    InferenceServiceQueryRequest,
    InferenceSessionCreateRequest,
    InferenceSessionQueryRequest,
    LabelUpdateRequest,
    ModelCreateRequest,
    ModelQueryRequest,
    ReportCreateRequest,
    ReportQueryRequest,
)


def _set_dyff_entity_placeholder_values(entity_dict: dict) -> None:
    entity_dict["id"] = ids.null_id()
    entity_dict["creationTime"] = datetime.datetime.utcfromtimestamp(0)
    entity_dict["status"] = "UNINITIALIZED"


def _stream_from_storage(path: str) -> fastapi.responses.StreamingResponse:
    def iterfile():
        with smart_open.open(path, "rb") as fin:
            yield from fin

    return fastapi.responses.StreamingResponse(iterfile())


def _stream_from_fileobj(fileobj: IO[bytes]) -> fastapi.responses.StreamingResponse:
    def iterfile(fileobj=fileobj):
        while data := fileobj.read(1024):
            yield data

    return fastapi.responses.StreamingResponse(iterfile())


class AutoRestAPIKeyHeader(fastapi.security.APIKeyHeader):
    """This functions the same way as ``OAuth2PasswordBearer``, but with
    ``scheme_name`` set to ``"AzureKey"``. For use with APIs for which we will
    generate client libraries using the autorest tool.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name="Authorization",
            scheme_name="AzureKey",
            description="API key authorization",
            **kwargs,
        )

    async def __call__(self, request: fastapi.Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None  # pragma: nocover
        return param


# ---------------------------------------------------------------------------


@functools.lru_cache()
def get_command_backend() -> CommandBackend:
    return dynamic_import.instantiate(config.api.command.backend)


@functools.lru_cache()
def get_query_backend() -> QueryBackend:
    return dynamic_import.instantiate(config.api.query.backend)


@functools.lru_cache()
def get_auth_backend() -> AuthBackend:
    return dynamic_import.instantiate(config.api.auth.backend)


@functools.lru_cache()
def get_gitlab_client() -> gitlab.Gitlab:
    return gitlab.Gitlab(
        private_token=config.gitlab.audit_reader_access_token.get_secret_value()
    )


@functools.lru_cache()
def get_security_scheme() -> AutoRestAPIKeyHeader:
    return AutoRestAPIKeyHeader()


@functools.lru_cache()
def get_api_key_signer() -> tokens.Signer:
    return tokens.get_signer(config.api.auth.api_key_signing_secret.get_secret_value())


# FIXME: We can't close the client because the FastAPI lifespan hooks only
# execute for the main server, and the API part is a sub-application. In the
# long run, we should separate the API server from the web content server so
# that they can be scaled independently.
# (It doesn't actually matter if we close the client because it only happens
# on application termination anyway :)
@functools.lru_cache()
def get_inference_async_client() -> httpx.AsyncClient:
    # Inference might take a (very) long time
    # TODO: Make configurable
    return httpx.AsyncClient(timeout=httpx.Timeout(5, read=None))


# ---------------------------------------------------------------------------


def archive_gitlab_directory(remote_path: Path, *, ref: str = "HEAD") -> io.BytesIO:
    def _file_size(f):
        f.seek(0, 2)
        file_size = f.tell()
        f.seek(0)
        return file_size

    project = get_gitlab_client().projects.get(
        config.storage.audit_leaderboards_gitlab_project
    )
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tgz:
        # The Gitlab API doesn't seem to distinguish between "directory empty" and
        # "directory not present". We're going to interpret "empty" as "missing"
        # and raise a 404.
        empty = True
        for d in project.repository_tree(path=str(remote_path), recursive=True):
            if d["type"] != "blob":
                continue

            empty = False
            remote_file = d["path"]
            # Strip directory prefix from remote path
            relative_file_path = Path(remote_file).relative_to(remote_path)

            blob = io.BytesIO()
            project.files.raw(remote_file, ref=ref, streamed=True, action=blob.write)

            info = tarfile.TarInfo(str(relative_file_path))
            info.size = _file_size(blob)
            tgz.addfile(info, blob)
        if empty:
            raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND)
    buffer.seek(0)
    return buffer


class Endpoint(NamedTuple):
    resource: str
    function: str

    @staticmethod
    def from_funcname(funcname: str) -> "Endpoint":
        resource, function = funcname.split("_")
        return Endpoint(resource=resource, function=function)


def get_endpoint(request: fastapi.Request) -> Endpoint:
    # This gets the Python function name that implements the endpoint. This is
    # the simplest way to determine which operation was requested (else we would
    # have to look at both the URL format and the method), and our names are
    # already constrained to be like 'resource_function' by the AutoRest tool.
    funcname = request.scope["route"].name
    return Endpoint.from_funcname(funcname)


def in_star(query: Optional[str], grant: Container[str]) -> bool:
    if query is None:
        return False
    return ("*" in grant) or (query in grant)


# Note: Actually call get_security_scheme() because the dependency is the thing
# that it returns.
def verify_api_key(
    token: str = fastapi.Depends(get_security_scheme()),
    auth_backend: AuthBackend = fastapi.Depends(get_auth_backend),
) -> APIKey:
    """Unpacks an API token into an APIKey object. Raises ``HTTPException(401)``
    if ``token`` is invalid.
    """
    try:
        return tokens.verify_api_token(
            token, get_api_key_signer(), auth_backend=auth_backend
        )
    except tokens.AuthenticationError as ex:
        # FIXME: See comment in alignmentlabs.dyff.web.server
        # logging.getLogger("api-server").exception("unauthorized")
        raise fastapi.HTTPException(
            fastapi.status.HTTP_401_UNAUTHORIZED,
            detail=str(ex),
            headers={"WWW-Authenticate": "Bearer"},
        )


def check_route_permissions(
    request: fastapi.Request, api_key: APIKey = fastapi.Depends(verify_api_key)
) -> None:
    """Checks permissions that can be checked when we only know the endpoint
    being called. This avoids making a DB query if the caller doesn't have
    permission for the endpoint. Raises ``HTTPException(401)`` if ``token`` is
    invalid, or ``HTTPException(403)`` if the token is valid but doesn't grant
    access to the requested endpoint.
    """
    # This gets the Python function name that implements the endpoint. This is
    # the simplest way to determine which operation was requested (else we would
    # have to look at both the URL format and the method), and our names are
    # already constrained to be like 'resource_function' by the AutoRest tool.
    path = request.scope["route"].name
    resource, function = path.split("_")

    for grant in api_key.grants:
        if (
            in_star(resource, grant.resources)
            # TODO: Can't currently check 'function' because APIFunctions
            # no longer corresponds 1-to-1 with endpoint names
            # and in_star(function, grant.functions)
            and (len(grant.accounts) > 0 or len(grant.entities) > 0)
        ):
            break
    else:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_403_FORBIDDEN,
            detail="API key does not grant access to this endpoint",
            headers={"WWW-Authenticate": "Bearer"},
        )


# New approach:
# 1. Build list of all accounts and entities that are granted for current resource + function
# 2. Create query constraints to limit results to those resources
# 3. Intersect user query with query constraints
# 3a. Short-circuit queries where we know the result set will be empty (e.g., user wants '?account=private' but doesn't have permission)


def is_endpoint_allowed(
    api_key: APIKey, endpoint: Endpoint, *, account: Optional[str], id: Optional[str]
) -> bool:
    for grant in api_key.grants:
        if (
            in_star(endpoint.resource, grant.resources)
            and in_star(endpoint.function, grant.functions)
            and (in_star(account, grant.accounts) or in_star(id, grant.entities))
        ):
            return True
    return False


def filter_forbidden_entities(
    api_key: APIKey, endpoint: Endpoint, entities: Iterable[DyffEntity]
) -> Iterable[DyffEntity]:
    """Filters a stream of ``DyffEntity`` objects to exclude entities that the
    provided ``APIKey`` does not grant permission to access.
    """
    for entity in entities:
        if is_endpoint_allowed(api_key, endpoint, account=entity.account, id=entity.id):
            yield entity


def check_endpoint_permissions(
    api_key: APIKey, endpoint: Endpoint, *, account: Optional[str], id: Optional[str]
):
    if not is_endpoint_allowed(api_key, endpoint, account=account, id=id):
        raise fastapi.HTTPException(
            fastapi.status.HTTP_403_FORBIDDEN,
            detail="API key does not grant access to this endpoint",
            headers={"WWW-Authenticate": "Bearer"},
        )


def check_endpoint_permissions_for_entity(
    api_key: APIKey, endpoint: Endpoint, entity: DyffModelWithID
):
    check_endpoint_permissions(api_key, endpoint, account=entity.account, id=entity.id)


def build_whitelist(api_key: APIKey, endpoint: Endpoint) -> Whitelist:
    accounts = set()
    entities = set()

    for grant in api_key.grants:
        if in_star(endpoint.resource, grant.resources) and in_star(
            endpoint.function, grant.functions
        ):
            accounts.update(grant.accounts)
            entities.update(grant.entities)

    return Whitelist(accounts=accounts, entities=entities)


_DyffEntityT = TypeVar("_DyffEntityT", bound=DyffEntity)


def require_entity_available(
    kind: Entities, id: str, entity: Optional[_DyffEntityT]
) -> _DyffEntityT:
    if entity is None:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_404_NOT_FOUND,
            f"referenced {kind} {id} not found",
        )
    elif is_status_terminal(entity.status) and not is_status_success(entity.status):
        raise fastapi.HTTPException(
            fastapi.status.HTTP_409_CONFLICT,
            f"referenced {kind} {id} unavailable: {entity.status} ({entity.reason})",
        )
    return entity


# ----------------------------------------------------------------------------


def _generate_unique_id(route: fastapi.routing.APIRoute) -> str:
    """Strip everything but the function name from the ``operationId`` fields."""
    return route.name


app = fastapi.FastAPI(
    title="Dyff API",
    generate_unique_id_function=_generate_unique_id,
    dependencies=[fastapi.Depends(check_route_permissions)],
)


# ----------------------------------------------------------------------------
# Endpoints

# @app.post("/token")
# def login():
#     # user_dict = fake_users_db.get(form_data.username)
#     # if not user_dict:
#     #     raise HTTPException(status_code=400, detail="Incorrect username or password")
#     # user = UserInDB(**user_dict)
#     # hashed_password = fake_hash_password(form_data.password)
#     # if not hashed_password == user.hashed_password:
#     #     raise HTTPException(status_code=400, detail="Incorrect username or password")
#     username = form_data.username
#     password = form_data.password
#     token = f"{username}:{password}"

#     return {"access_token": token, "token_type": "bearer"}

# ----------------------------------------------------------------------------


@app.patch(
    f"/{Resources.Audit}/{{audit_id}}/labels",
    tags=[Resources.Audit],
    summary="Update labels for an existing Audit.",
)
def audits_label(
    audit_id: str,
    label_request: LabelUpdateRequest,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    audit = query_backend.get_audit(audit_id)
    if audit is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, audit)
    return command_backend.update_labels(audit_id, label_request)


@app.get(
    f"/{Resources.Audit}",
    tags=[Resources.Audit],
    summary="Get all Audits matching a query.",
    response_description="The Audits matching the query.",
)
def audits_query(
    query: AuditQueryRequest = fastapi.Depends(),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> list[Audit]:
    """Get all Audits matching a query. The query is a set of equality
    constraints specified as key-value pairs.
    """
    whitelist = build_whitelist(api_key, endpoint)
    results = query_backend.query_audits(whitelist, query)
    return list(results)


@app.get(
    f"/{Resources.Audit}/{{audit_id}}",
    tags=[Resources.Audit],
    summary="Get an Audit by its key.",
    response_description="The Audit with the given key.",
)
def audits_get(
    audit_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Audit:
    """Get an Audit by its key. Raises a 404 error if no entity exists with that key."""
    audit = query_backend.get_audit(audit_id)
    if audit is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, audit)
    return audit


@app.post(
    f"/{Resources.Audit}/{{audit_id}}/upload",
    tags=[Resources.Audit],
    response_class=fastapi.Response,
    summary="Upload an Audit report.",
)
def audits_upload(
    audit_id: str,
    # Note: autorest breaks if you don't provide a 'description':
    # File "@autorestpython@6.4.9/node_modules/@autorest/python/autorest/m4reformatter/__init__.py", line 471, in update_parameterbase
    #   "description": yaml_data["language"]["default"]["description"],
    # KeyError: 'description'
    file: fastapi.UploadFile = fastapi.File(
        ..., description=".tar.gz archive of rendered audit report"
    ),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    try:
        audit = query_backend.get_audit(audit_id)
        if audit is None:
            raise fastapi.HTTPException(
                fastapi.status.HTTP_404_NOT_FOUND, f"Audit {audit_id} not found"
            )
        check_endpoint_permissions_for_entity(api_key, endpoint, audit)
        with tarfile.open(fileobj=file.file, mode="r:gz") as tgz:
            for member in tgz:
                path = sanitize_relative_file_path(member.name)
                member_file = tgz.extractfile(str(path))
                if member_file is None:
                    raise ValueError(f"archive path {path} is not a file")
                member_bytes = member_file.read()
                storage_path = f"{storage.paths.auditreport_root(audit_id)}/{path}"
                with smart_open.open(storage_path, "wb") as fout:
                    fout.write(member_bytes)
    except fastapi.HTTPException:
        raise
    except Exception as ex:
        msg = "Upload must be a .tar.gz archive"
        # FIXME: See comment in alignmentlabs.dyff.web.server
        # logging.getLogger("api-server").exception(msg)
        raise fastapi.HTTPException(
            fastapi.status.HTTP_400_BAD_REQUEST, detail=msg
        ) from ex
    finally:
        file.file.close()


@app.put(
    f"/{Resources.Audit}/{{audit_id}}/delete",
    tags=[Resources.Audit],
    summary="Mark an Audit for deletion.",
    response_description="The resulting status of the entity.",
)
def audits_delete(
    audit_id: str,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Status:
    audit = query_backend.get_audit(audit_id)
    if audit is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, audit)
    if audit.status != EntityStatus.deleted:
        command_backend.delete_entity(audit_id)
        return Status(
            status=EntityStatus.deleted, reason=EntityStatusReason.delete_command
        )
    else:
        return Status(status=audit.status, reason=audit.reason)


# ----------------------------------------------------------------------------


@app.get(
    f"/{Resources.AuditProcedure}/{{path:path}}/download",
    tags=[Resources.AuditProcedure],
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {},
        # Note: If you use 'application/octet-stream', fastapi also generates an
        # (empty) 'application/json' schema in the OpenAPI spec, which confuses
        # the autorest tool. This here works even though the content isn't JSON.
        # See: https://github.com/Azure/autorest/blob/main/docs/openapi/howto/binary-payload.md
        fastapi.status.HTTP_200_OK: {
            "content": {
                "application/json": {"schema": {"type": "string", "format": "binary"}}
            }
        },
    },
    summary="Download the source code of an AuditProcedure.",
)
def auditprocedures_download(
    path: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    # FIXME: SECURITY Need to check premissions
    # auditprocedure = query_backend.get_audit_procedure(item_id)
    # if auditprocedure is None:
    #   raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, f"AuditProcedure {item_id} not found")
    # check_entity_permissions(api_key, endpoint, auditprocedure)
    return _stream_from_fileobj(archive_gitlab_directory(Path(path)))


# ----------------------------------------------------------------------------


@app.patch(
    f"/{Resources.Dataset}/{{dataset_id}}/labels",
    tags=[Resources.Dataset],
    summary="Update labels for an existing Dataset.",
)
def datasets_label(
    dataset_id: str,
    label_request: LabelUpdateRequest,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    dataset = query_backend.get_dataset(dataset_id)
    if dataset is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, dataset)
    return command_backend.update_labels(dataset_id, label_request)


@app.get(
    f"/{Resources.Dataset}",
    tags=[Resources.Dataset],
    summary="Get all Datasets matching a query.",
    response_description="The Datasets matching the query.",
)
def datasets_query(
    query: DatasetQueryRequest = fastapi.Depends(),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> list[Dataset]:
    """Get all Datasets matching a query. The query is a set of equality
    constraints specified as key-value pairs.
    """
    whitelist = build_whitelist(api_key, endpoint)
    results = query_backend.query_datasets(whitelist, query)
    return list(results)


@app.get(
    f"/{Resources.Dataset}/{{dataset_id}}",
    tags=[Resources.Dataset],
    summary="Get a Dataset by its key.",
    response_description="The Dataset with the given key.",
)
def datasets_get(
    dataset_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Dataset:
    """Get a Dataset by its key. Raises a 404 error if no entity exists with that key."""
    dataset = query_backend.get_dataset(dataset_id)
    if dataset is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, dataset)
    return dataset


@app.get(
    f"/{Resources.Dataset}/{{dataset_id}}/strata",
    tags=[Resources.Dataset],
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {},
        # Note: If you use 'application/octet-stream', fastapi also generates an
        # (empty) 'application/json' schema in the OpenAPI spec, which confuses
        # the autorest tool. This here works even though the content isn't JSON.
        # See: https://github.com/Azure/autorest/blob/main/docs/openapi/howto/binary-payload.md
        fastapi.status.HTTP_200_OK: {
            "content": {
                "application/json": {"schema": {"type": "string", "format": "binary"}}
            }
        },
    },
    summary="Get the strata corresponding to a Dataset.",
    response_description="A Parquet file containing the strata information.",
)
def datasets_strata(
    dataset_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    """Get the strata corresponding to a Dataset. The data is returned as a
    Parquet file suitable for reading with libraries like Pandas.
    """
    dataset = query_backend.get_dataset(dataset_id)
    if dataset is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, dataset)
    # FIXME: Handle multi-file data (or choose a better name than 'part-0')
    return _stream_from_storage(storage.paths.dataset_strata(dataset_id))


@app.get(
    f"/{Resources.Dataset}/{{dataset_id}}/data",
    tags=[Resources.Dataset],
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {},
        # Note: If you use 'application/octet-stream', fastapi also generates an
        # (empty) 'application/json' schema in the OpenAPI spec, which confuses
        # the autorest tool. This here works even though the content isn't JSON.
        # See: https://github.com/Azure/autorest/blob/main/docs/openapi/howto/binary-payload.md
        fastapi.status.HTTP_200_OK: {
            "content": {
                "application/json": {"schema": {"type": "string", "format": "binary"}}
            }
        },
    },
    summary="Get the raw data for the Dataset.",
    response_description="A byte stream in pyarrow.ipc format.",
)
def datasets_data(
    dataset_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    """Get the raw data for the Dataset. The data is streamed in pyarrow.ipc
    format."""
    dataset = query_backend.get_dataset(dataset_id)
    if dataset is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, dataset)

    def bytes_generator():
        ds = arrow.open_dataset(storage.paths.dataset_root(dataset_id))
        sink = pyarrow.BufferOutputStream()
        with pyarrow.ipc.new_stream(sink, ds.schema) as writer:
            for batch in ds.to_batches():
                writer.write_batch(batch)
        # This is not great because it copies the buffer, but I can't figure out
        # how to make StreamingResponse consume the PyArrow buffer directly.
        yield sink.getvalue().to_pybytes()

    return fastapi.responses.StreamingResponse(bytes_generator())


# Problem: Since we can't revoke signed URLs, there is a window where the dataset
# could be altered after the initial upload. A malicious user could upload a
# manipulated Dataset, run an Evaluation on the Dataset and get a good result,
# then replace the Dataset with a legitimate one.
#
# Solution: The user specifies the checksum of the data when creating the
# Dataset record. Consumers of the Dataset verify the checksum.
#
# 1. User calls POST /datasets {"artifacts": [Artifact]} and gets a new Dataset record in Created status
#    a. Server creates .dyff/artifacts.json in <bucket>/<id>/
#    b. Server produces Create event
# 2. User calls GET /datasets/<id>/upload/<artifact-name> -> signed upload URL
# 3. User uploads the file using the signed URL
# 4. User calls POST /datasets/<id>/finalize
#    a. Server checks that all artifacts are uploaded and match provided checksum
#    b. Server produces .status event
# 5. Dataset consumers verify artifact digests against the GCS Blob.md5_hash
@app.post(
    f"/{Resources.Dataset}",
    tags=[Resources.Dataset],
    summary="Create a Dataset.",
    response_description="The created Dataset entity.",
)
def datasets_create(
    dataset_request: DatasetCreateRequest,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Dataset:
    # Check permission to create evaluations
    check_endpoint_permissions(
        api_key, endpoint, account=dataset_request.account, id=None
    )
    # FIXME: This is (possibly?) gcloud-specific -- gcloud only provides md5 hashes
    if any(artifact.digest.md5 is None for artifact in dataset_request.artifacts):
        raise fastapi.HTTPException(
            fastapi.status.HTTP_400_BAD_REQUEST,
            "gcloud storage requires artifact.digest.md5",
        )
    dataset_dict = dataset_request.dict()
    _set_dyff_entity_placeholder_values(dataset_dict)
    dataset = Dataset.parse_obj(dataset_dict)
    return command_backend.create_dataset(dataset)


@app.put(
    f"/{Resources.Dataset}/{{dataset_id}}/delete",
    tags=[Resources.Dataset],
    summary="Mark a Dataset for deletion.",
    response_description="The resulting status of the entity.",
)
def datasets_delete(
    dataset_id: str,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Status:
    dataset = query_backend.get_dataset(dataset_id)
    if dataset is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, dataset)
    if dataset.status != EntityStatus.deleted:
        command_backend.delete_entity(dataset_id)
        return Status(
            status=EntityStatus.deleted, reason=EntityStatusReason.delete_command
        )
    else:
        return Status(status=dataset.status, reason=dataset.reason)


@app.get(
    f"/{Resources.Dataset}/{{dataset_id}}/upload/{{artifact_path:path}}",
    tags=[Resources.Dataset],
    summary="Get a signed URL to which the given artifact can be uploaded.",
    response_description="A signed upload URL.",
)
def datasets_upload(
    dataset_id: str,
    artifact_path: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> StorageSignedURL:
    dataset = query_backend.get_dataset(dataset_id)
    if dataset is None:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_404_NOT_FOUND, f"no dataset {dataset_id}"
        )
    check_endpoint_permissions_for_entity(api_key, endpoint, dataset)
    if dataset.status != DatasetStatus.created:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_409_CONFLICT,
            f"expected dataset.status == {DatasetStatus.created}; got {dataset.status}",
        )
    for artifact in dataset.artifacts:
        if artifact.path == artifact_path:
            break
    else:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_404_NOT_FOUND, f"no artifact {artifact} in dataset"
        )
    return storage.signed_url_for_dataset_upload(dataset_id, artifact)


@app.post(
    f"/{Resources.Dataset}/{{dataset_id}}/finalize",
    tags=[Resources.Dataset],
    summary="Indicate that all dataset artifacts have been uploaded.",
    response_description="A signed upload URL.",
)
def datasets_finalize(
    dataset_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> None:
    dataset = query_backend.get_dataset(dataset_id)
    if dataset is None:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_404_NOT_FOUND, f"no dataset {dataset_id}"
        )
    check_endpoint_permissions_for_entity(api_key, endpoint, dataset)

    if dataset.status == DatasetStatus.ready:
        return
    elif dataset.status != DatasetStatus.created:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_409_CONFLICT,
            f"expected dataset.status == {DatasetStatus.created}; got {dataset.status}",
        )

    for artifact in dataset.artifacts:
        if artifact.digest.md5 is None:
            raise fastapi.HTTPException(
                fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"artifact.digest.md5 is None; this should have been caught at dataset creation",
            )
        storage_md5 = storage.dataset_artifact_md5hash(dataset_id, artifact.path)
        if storage_md5 != base64.b64decode(artifact.digest.md5):
            raise fastapi.HTTPException(
                fastapi.status.HTTP_409_CONFLICT, f"artifact hash {artifact.path}"
            )

    artifacts_dict = dataset.dict()["artifacts"]
    artifacts_json = json.dumps(artifacts_dict)
    with smart_open.open(
        f"{storage.paths.dataset_root(dataset.id)}/.dyff/artifacts.json", "w"
    ) as artifacts_json_out:
        artifacts_json_out.write(artifacts_json)
    command_backend.update_status(dataset_id, status=DatasetStatus.ready)


# ----------------------------------------------------------------------------


@app.patch(
    f"/{Resources.Evaluation}/{{evaluation_id}}/labels",
    tags=[Resources.Evaluation],
    summary="Update labels for an existing Evaluation.",
)
def evaluations_label(
    evaluation_id: str,
    label_request: LabelUpdateRequest,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    evaluation = query_backend.get_evaluation(evaluation_id)
    if evaluation is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, evaluation)
    return command_backend.update_labels(evaluation_id, label_request)


@app.get(
    f"/{Resources.Evaluation}",
    tags=[Resources.Evaluation],
    summary="Get all Evaluations matching a query.",
    response_description="The Evaluations matching the query.",
)
def evaluations_query(
    query: EvaluationQueryRequest = fastapi.Depends(),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> list[Evaluation]:
    """Get all Evaluations matching a query. The query is a set of equality
    constraints specified as key-value pairs.
    """
    whitelist = build_whitelist(api_key, endpoint)
    results = query_backend.query_evaluations(whitelist, query)
    return list(results)


@app.get(
    f"/{Resources.Evaluation}/{{evaluation_id}}",
    tags=[Resources.Evaluation],
    summary="Get an Evaluation by its key.",
    response_description="The Evaluation with the given key.",
)
def evaluations_get(
    evaluation_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Evaluation:
    """Get an Evaluation by its key. Raises a 404 error if no entity exists with that key."""
    evaluation = query_backend.get_evaluation(evaluation_id)
    if evaluation is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, evaluation)
    return evaluation


@app.post(
    f"/{Resources.Evaluation}",
    tags=[Resources.Evaluation],
    summary="Create an Evaluation.",
    response_description="The created Evaluation entity.",
)
def evaluations_create(
    evaluation_request: EvaluationCreateRequest,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Evaluation:
    # Check permission to create evaluations
    check_endpoint_permissions(
        api_key, endpoint, account=evaluation_request.account, id=None
    )
    # Referenced InferenceService
    service_id = evaluation_request.inferenceSession.inferenceService
    service = query_backend.get_inference_service(service_id)
    service = require_entity_available(Entities.InferenceService, service_id, service)
    # Check permission to consume referenced InferenceService
    check_endpoint_permissions_for_entity(
        api_key,
        Endpoint(
            resource=Resources.InferenceService.value,
            function=APIFunctions.consume.value,
        ),
        service,
    )

    # Referenced Dataset
    dataset_id = evaluation_request.dataset
    dataset = query_backend.get_dataset(dataset_id)
    dataset = require_entity_available(Entities.Dataset, dataset_id, dataset)
    # Check permission to consume referenced Dataset
    check_endpoint_permissions_for_entity(
        api_key,
        Endpoint(resource=Resources.Dataset.value, function=APIFunctions.consume.value),
        dataset,
    )

    evaluation_dict = evaluation_request.dict()
    _set_dyff_entity_placeholder_values(evaluation_dict)
    evaluation_dict["inferenceSession"]["inferenceService"] = service.dict()
    evaluation = Evaluation.parse_obj(evaluation_dict)
    return command_backend.create_evaluation(evaluation)


@app.put(
    f"/{Resources.Evaluation}/{{evaluation_id}}/delete",
    tags=[Resources.Evaluation],
    summary="Mark an Evaluation for deletion.",
    response_description="The resulting status of the entity.",
)
def evaluations_delete(
    evaluation_id: str,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Status:
    evaluation = query_backend.get_evaluation(evaluation_id)
    if evaluation is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, evaluation)
    if evaluation.status != EntityStatus.deleted:
        command_backend.delete_entity(evaluation_id)
        return Status(
            status=EntityStatus.deleted, reason=EntityStatusReason.delete_command
        )
    else:
        return Status(status=evaluation.status, reason=evaluation.reason)


# ----------------------------------------------------------------------------


@app.patch(
    f"/{Resources.InferenceService}/{{service_id}}/labels",
    tags=[Resources.InferenceService],
    summary="Update labels for an existing InferenceService.",
)
def inferenceservices_label(
    service_id: str,
    label_request: LabelUpdateRequest,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    service = query_backend.get_inference_service(service_id)
    if service is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, service)
    return command_backend.update_labels(service_id, label_request)


@app.get(
    f"/{Resources.InferenceService}",
    tags=[Resources.InferenceService],
    summary="Get all InferenceServices matching a query.",
    response_description="The InferenceServices matching the query.",
)
def inferenceservices_query(
    query: InferenceServiceQueryRequest = fastapi.Depends(),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> list[InferenceService]:
    """Get all InferenceServices matching a query. The query is a set of equality
    constraints specified as key-value pairs.
    """
    whitelist = build_whitelist(api_key, endpoint)
    results = query_backend.query_inference_services(whitelist, query)
    return list(results)


@app.get(
    f"/{Resources.InferenceService}/{{service_id}}",
    tags=[Resources.InferenceService],
    summary="Get an InferenceService by its key.",
    response_description="The InferenceService with the given key.",
)
def inferenceservices_get(
    service_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> InferenceService:
    """Get an InferenceService by its key. Raises a 404 error if no entity exists with that key."""
    inferenceservice = query_backend.get_inference_service(service_id)
    if inferenceservice is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, inferenceservice)
    return inferenceservice


@app.post(
    f"/{Resources.InferenceService}",
    tags=[Resources.InferenceService],
    summary="Create an InferenceService.",
    response_description="The created InferenceService entity.",
)
def inferenceservices_create(
    inference_service_request: InferenceServiceCreateRequest,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> InferenceService:
    # Check permission to create InferenceSession
    check_endpoint_permissions(
        api_key, endpoint, account=inference_service_request.account, id=None
    )
    # Referenced Model
    if inference_service_request.model is not None:
        model_id = inference_service_request.model
        model = query_backend.get_model(model_id)
        model = require_entity_available(Entities.Model, model_id, model)
        # Check permission to consume referenced Model
        check_endpoint_permissions_for_entity(
            api_key,
            Endpoint(
                resource=Resources.Model.value, function=APIFunctions.consume.value
            ),
            model,
        )
    else:
        model = None

    service_dict = inference_service_request.dict()
    _set_dyff_entity_placeholder_values(service_dict)
    service_dict["model"] = model and model.dict()
    inference_service = InferenceService.parse_obj(service_dict)
    return command_backend.create_inference_service(inference_service)


@app.put(
    f"/{Resources.InferenceService}/{{service_id}}/delete",
    tags=[Resources.InferenceService],
    summary="Mark an InferenceService for deletion.",
    response_description="The resulting status of the entity.",
)
def inferenceservices_delete(
    service_id: str,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Status:
    service = query_backend.get_inference_service(service_id)
    if service is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, service)
    if service.status != EntityStatus.deleted:
        command_backend.delete_entity(service_id)
        return Status(
            status=EntityStatus.deleted, reason=EntityStatusReason.delete_command
        )
    else:
        return Status(status=service.status, reason=service.reason)


# ----------------------------------------------------------------------------


@app.patch(
    f"/{Resources.InferenceSession}/{{session_id}}/labels",
    tags=[Resources.InferenceSession],
    summary="Update labels for an existing InferenceSession.",
)
def inferencesessions_label(
    session_id: str,
    label_request: LabelUpdateRequest,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    session = query_backend.get_inference_session(session_id)
    if session is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, session)
    return command_backend.update_labels(session_id, label_request)


@app.get(
    f"/{Resources.InferenceSession}",
    tags=[Resources.InferenceSession],
    summary="Get all InferenceSessions matching a query.",
    response_description="The InferenceSessions matching the query.",
)
def inferencesessions_query(
    query: InferenceSessionQueryRequest = fastapi.Depends(),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> list[InferenceSession]:
    """Get all InferenceSessions matching a query. The query is a set of equality
    constraints specified as key-value pairs.
    """
    whitelist = build_whitelist(api_key, endpoint)
    results = query_backend.query_inference_sessions(whitelist, query)
    return list(results)


@app.get(
    f"/{Resources.InferenceSession}/{{session_id}}",
    tags=[Resources.InferenceSession],
    summary="Get an InferenceSession by its key.",
    response_description="The InferenceSession with the given key.",
)
def inferencesessions_get(
    session_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> InferenceSession:
    """Get an InferenceSession by its key. Raises a 404 error if no entity exists with that key."""
    inference_session = query_backend.get_inference_session(session_id)
    if inference_session is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, inference_session)
    return inference_session


# func (r *InferenceSessionReconciler) inferenceServiceAddress(inferencesession *dyffv1alpha1.InferenceSession) string {
# 	var builder strings.Builder
# 	builder.WriteString("http://")
# 	builder.WriteString(inferencesession.Name)
# 	builder.WriteString(".")
# 	builder.WriteString(inferencesession.Namespace)
# 	builder.WriteString(":80")
# 	return builder.String()
# }


def _create_session_token(
    *, session: str, account: str, expires: Optional[datetime.datetime]
) -> str:
    if expires is None:
        expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    grant = AccessGrant(
        resources=[Resources.InferenceSession],
        functions=[APIFunctions.get, APIFunctions.consume, APIFunctions.terminate],
        entities=[session],
    )
    session_key = tokens.generate_api_key(
        subject_type=Entities.Account,
        subject_id=account,
        grants=[grant],
        expires=expires,
    )
    return get_api_key_signer().sign_api_key(session_key)


def _session_internal_endpoint(session_id: str, session_endpoint: str) -> str:
    return f"http://session-{session_id}.{config.kubernetes.workflows_namespace}:80/{session_endpoint}"


@app.post(
    f"/{Resources.InferenceSession}",
    tags=[Resources.InferenceSession],
    summary="Create an InferenceSession.",
    response_description="The created InferenceSession entity.",
)
def inferencesessions_create(
    inference_session_request: InferenceSessionCreateRequest,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> InferenceSessionAndToken:
    # inferencesessions.create for request account
    check_endpoint_permissions(
        api_key, endpoint, account=inference_session_request.account, id=None
    )
    # Referenced InferenceService
    service_id = inference_session_request.inferenceService
    service = query_backend.get_inference_service(service_id)
    service = require_entity_available(Entities.InferenceService, service_id, service)
    # inferenceservices.consume for referenced service
    check_endpoint_permissions_for_entity(
        api_key,
        Endpoint(
            resource=Resources.InferenceService.value,
            function=APIFunctions.consume.value,
        ),
        service,
    )

    session_dict = inference_session_request.dict()
    _set_dyff_entity_placeholder_values(session_dict)
    # This works because ForeignInferenceService is a subset of InferenceService
    session_dict["inferenceService"] = service.dict()
    inference_session = InferenceSession.parse_obj(session_dict)
    inference_session = command_backend.create_inference_session(inference_session)

    try:
        session_token = _create_session_token(
            session=inference_session.id,
            account=inference_session.account,
            expires=inference_session.expires,
        )
        return InferenceSessionAndToken(
            inferencesession=inference_session, token=session_token
        )
    except Exception as ex:
        command_backend.terminate_workflow(inference_session.id)
        raise fastapi.HTTPException(
            fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to generate session token",
        ) from ex


@app.put(
    f"/{Resources.InferenceSession}/{{session_id}}/delete",
    tags=[Resources.InferenceSession],
    summary="Mark an InferenceSession for deletion.",
    response_description="The resulting status of the entity.",
)
def inferencesessions_delete(
    session_id: str,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Status:
    session = query_backend.get_inference_session(session_id)
    if session is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, session)
    if session.status != EntityStatus.deleted:
        command_backend.delete_entity(session_id)
        return Status(
            status=EntityStatus.deleted, reason=EntityStatusReason.delete_command
        )
    else:
        return Status(status=session.status, reason=session.reason)


@app.put(
    f"/{Resources.InferenceSession}/{{session_id}}/terminate",
    tags=[Resources.InferenceSession],
    summary="Terminate an InferenceSession.",
)
def inferencesessions_terminate(
    session_id: str,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Status:
    session = query_backend.get_inference_session(session_id)
    if session is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, session)
    if session.status != EntityStatus.terminated:
        command_backend.terminate_workflow(session_id)
        return Status(
            status=EntityStatus.terminated, reason=EntityStatusReason.terminate_command
        )
    else:
        return Status(status=session.status, reason=session.reason)


@app.post(
    f"/{Resources.InferenceSession}/{{session_id}}/infer/{{inference_endpoint:path}}",
    tags=[Resources.InferenceSession],
    summary="Create an InferenceSession.",
    response_description="The created InferenceSession entity.",
)
async def inferencesessions_infer(
    session_id: str,
    inference_endpoint: str,
    request: fastapi.Request,  # TODO: Define schemas for inference inputs
    inference_client: httpx.AsyncClient = fastapi.Depends(get_inference_async_client),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> fastapi.responses.StreamingResponse:
    # Note: Passing None for account means that the API key must have access
    # to this resource by ID. API keys associated with accounts won't work here.
    check_endpoint_permissions(
        api_key,
        Endpoint(resource=Resources.InferenceSession, function=APIFunctions.consume),
        id=session_id,
        account=None,
    )
    # FIXME: Define this URL in a canonical location
    # TODO: Should we expose the sessions at opaque IPs so that we don't need
    # to know that we're running in Kubernetes?
    internal_endpoint = _session_internal_endpoint(session_id, inference_endpoint)
    url = httpx.URL(internal_endpoint, query=request.url.query.encode("utf-8"))
    proxy_request = inference_client.build_request(
        request.method, url, headers=request.headers.raw, content=await request.body()
    )
    proxy_response = await inference_client.send(proxy_request, stream=True)
    return fastapi.responses.StreamingResponse(
        proxy_response.aiter_raw(),
        status_code=proxy_response.status_code,
        headers=proxy_response.headers,
        background=starlette.background.BackgroundTask(proxy_response.aclose),
    )


@app.get(
    f"/{Resources.InferenceSession}/{{session_id}}/token",
    tags=[Resources.InferenceSession],
    summary="Get an access token for an existing InferenceSession.",
    response_description="A session access token.",
)
def inferencesessions_token(
    session_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
) -> str:
    session = query_backend.get_inference_session(session_id)
    if session is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    # inferencesessions.get
    check_endpoint_permissions_for_entity(
        api_key,
        Endpoint(
            resource=Resources.InferenceSession.value,
            function=APIFunctions.get.value,
        ),
        session,
    )
    # inferenceservices.consume for referenced service
    check_endpoint_permissions_for_entity(
        api_key,
        Endpoint(
            resource=Resources.InferenceService.value,
            function=APIFunctions.consume.value,
        ),
        session.inferenceService,
    )

    try:
        return _create_session_token(
            session=session.id,
            account=session.account,
            expires=session.expires,
        )
    except Exception as ex:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to generate session token",
        ) from ex


@app.get(
    f"/{Resources.InferenceSession}/{{session_id}}/ready",
    tags=[Resources.InferenceSession],
    summary="Perform a readiness probe on the session.",
    response_description="HTTP 200 if ready, 503 or other appropriate error if not ready.",
)
async def inferencesessions_ready(
    session_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    inference_client: httpx.AsyncClient = fastapi.Depends(get_inference_async_client),
    api_key: APIKey = fastapi.Depends(verify_api_key),
) -> fastapi.Response:
    """Check if an InferenceSession is ready. Returns status 200 if the
    session is ready. Raises a 503 (ServiceUnavailable) error if the session
    is not ready.

    Raises a 404 error if no session exists with the provided ID. Note that
    this may happen temporarily for session that were created recently, as it
    takes time for status information to propagate through the platform.
    """
    inference_session = query_backend.get_inference_session(session_id)
    if inference_session is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    # inferencesessions.get
    # We consider /ready to be an aspect of get
    # Note: We might want to not check permissions for /ready at all, since
    # it doesn't provide any sensitive information and we have to do a DB
    # query to perform the check.
    check_endpoint_permissions_for_entity(
        api_key,
        Endpoint(
            resource=Resources.InferenceSession,
            function=APIFunctions.get,
        ),
        inference_session,
    )

    internal_endpoint = _session_internal_endpoint(session_id, "ready")
    url = httpx.URL(internal_endpoint)
    # Short timeout because the pod could still be in a Pending status, so
    # instead of returning "not ready", the request will just time out.
    request = inference_client.build_request("GET", url, timeout=httpx.Timeout(0.5))
    try:
        response = await inference_client.send(request)
        response.raise_for_status()
    except httpx.HTTPError:
        return fastapi.Response(status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE)
    return fastapi.Response(status_code=fastapi.status.HTTP_200_OK)


# ----------------------------------------------------------------------------


@app.patch(
    f"/{Resources.Model}/{{model_id}}/labels",
    tags=[Resources.Model],
    summary="Update labels for an existing Model.",
)
def models_label(
    model_id: str,
    label_request: LabelUpdateRequest,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    model = query_backend.get_model(model_id)
    if model is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, model)
    return command_backend.update_labels(model_id, label_request)


@app.get(
    f"/{Resources.Model}",
    tags=[Resources.Model],
    summary="Get all Models matching a query.",
    response_description="The Models matching the query.",
)
def models_query(
    query: ModelQueryRequest = fastapi.Depends(),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> list[Model]:
    """Get all Models matching a query. The query is a set of equality
    constraints specified as key-value pairs.
    """
    whitelist = build_whitelist(api_key, endpoint)
    results = query_backend.query_models(whitelist, query)
    return list(results)


@app.get(
    f"/{Resources.Model}/{{model_id}}",
    tags=[Resources.Model],
    summary="Get a Model by its key.",
    response_description="The Model with the given key.",
)
def models_get(
    model_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Model:
    """Get a Model by its key. Raises a 404 error if no entity exists with that key."""
    model = query_backend.get_model(model_id)
    if model is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, model)
    return model


@app.post(
    f"/{Resources.Model}",
    tags=[Resources.Model],
    summary="Create a Model.",
    response_description="The created Model entity.",
)
def models_create(
    model_request: ModelCreateRequest,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Model:
    # Check permission to create models
    check_endpoint_permissions(
        api_key, endpoint, account=model_request.account, id=None
    )

    model_dict = model_request.dict()
    _set_dyff_entity_placeholder_values(model_dict)
    model = Model.parse_obj(model_dict)
    return command_backend.create_model(model)


@app.put(
    f"/{Resources.Model}/{{model_id}}/delete",
    tags=[Resources.Model],
    summary="Mark a Model for deletion.",
    response_description="The resulting status of the entity.",
)
def models_delete(
    model_id: str,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Status:
    model = query_backend.get_model(model_id)
    if model is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, model)
    if model.status != EntityStatus.deleted:
        command_backend.delete_entity(model_id)
        return Status(
            status=EntityStatus.deleted, reason=EntityStatusReason.delete_command
        )
    else:
        return Status(status=model.status, reason=model.reason)


# ----------------------------------------------------------------------------


@app.patch(
    f"/{Resources.Report}/{{report_id}}/labels",
    tags=[Resources.Report],
    summary="Update labels for an existing Report.",
)
def reports_label(
    report_id: str,
    label_request: LabelUpdateRequest,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    report = query_backend.get_report(report_id)
    if report is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, report)
    return command_backend.update_labels(report_id, label_request)


@app.get(
    f"/{Resources.Report}",
    tags=[Resources.Report],
    summary="Get all Reports matching a query.",
    response_description="The Reports matching the query.",
)
def reports_query(
    query: ReportQueryRequest = fastapi.Depends(),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> list[Report]:
    """Get all Reports matching a query. The query is a set of equality
    constraints specified as key-value pairs.
    """
    whitelist = build_whitelist(api_key, endpoint)
    results = query_backend.query_reports(whitelist, query)
    return list(results)


@app.get(
    f"/{Resources.Report}/{{report_id}}",
    tags=[Resources.Report],
    summary="Get a Report by its key.",
    response_description="The Report with the given key.",
)
def reports_get(
    report_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Report:
    """Get a Report by its key. Raises a 404 error if no entity exists with that key."""
    report = query_backend.get_report(report_id)
    if report is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, report)
    return report


@app.post(
    f"/{Resources.Report}",
    tags=[Resources.Report],
    summary="Create a Report.",
    response_description="The created Report entity.",
)
def reports_create(
    report_request: ReportCreateRequest,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Report:
    # Check permission to create reports
    check_endpoint_permissions(
        api_key, endpoint, account=report_request.account, id=None
    )

    # Referenced Evaluation
    evaluation_id = report_request.evaluation
    evaluation = query_backend.get_evaluation(evaluation_id)
    evaluation = require_entity_available(
        Entities.Evaluation, evaluation_id, evaluation
    )
    evaluation_view = None
    if isinstance(report_request.evaluationView, str):
        service = evaluation.inferenceSession.inferenceService
        for view in service.outputViews:
            if view.id == report_request.evaluationView:
                evaluation_view = view
                break
        else:
            raise fastapi.HTTPException(
                fastapi.status.HTTP_404_NOT_FOUND,
                f"no View with .id {report_request.evaluationView}"
                f" for InferenceService {service.id}",
            )
    else:
        # Also covers the case where evaluationView is None
        evaluation_view = report_request.evaluationView
    # Check permission to consume referenced Evaluation
    check_endpoint_permissions_for_entity(
        api_key,
        Endpoint(
            resource=Resources.Evaluation.value, function=APIFunctions.consume.value
        ),
        evaluation,
    )

    # Referenced Dataset
    dataset_id = evaluation.dataset
    dataset = query_backend.get_dataset(dataset_id)
    dataset = require_entity_available(Entities.Dataset, dataset_id, dataset)
    dataset_view = None
    if isinstance(report_request.datasetView, str):
        for view in dataset.views:
            if view.id == report_request.datasetView:
                dataset_view = view
                break
        else:
            raise fastapi.HTTPException(
                fastapi.status.HTTP_404_NOT_FOUND,
                f"no View with .id {report_request.datasetView} for Dataset {dataset.id}",
            )
    else:
        # Also covers the case where datasetView is None
        dataset_view = report_request.datasetView
    # Check permission to consume referenced InferenceService
    check_endpoint_permissions_for_entity(
        api_key,
        Endpoint(
            resource=Resources.Dataset.value,
            # TODO: There need to be separate roles for consuming input
            # instances vs. consuming labels and covariates, and Dataset needs
            # a way to annotate which category each field belongs to.
            function=APIFunctions.consume.value,
        ),
        dataset,
    )

    report_dict = report_request.dict()
    _set_dyff_entity_placeholder_values(report_dict)
    service = evaluation.inferenceSession.inferenceService
    report_dict["dataset"] = dataset.id
    report_dict["inferenceService"] = service.id
    report_dict["model"] = service.model.id if service.model else None
    report_dict["datasetView"] = dataset_view and dataset_view.dict()
    report_dict["evaluationView"] = evaluation_view and evaluation_view.dict()
    report = Report.parse_obj(report_dict)
    return command_backend.create_report(report)


@app.put(
    f"/{Resources.Report}/{{report_id}}/delete",
    tags=[Resources.Report],
    summary="Mark a Report for deletion.",
    response_description="The resulting status of the entity.",
)
def reports_delete(
    report_id: str,
    command_backend: CommandBackend = fastapi.Depends(get_command_backend),
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
) -> Status:
    report = query_backend.get_report(report_id)
    if report is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, report)
    if report.status != EntityStatus.deleted:
        command_backend.delete_entity(report_id)
        return Status(
            status=EntityStatus.deleted, reason=EntityStatusReason.delete_command
        )
    else:
        return Status(status=report.status, reason=report.reason)


@app.get(
    f"/{Resources.Report}/{{report_id}}/data",
    tags=[Resources.Report],
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {},
        # Note: If you use 'application/octet-stream', fastapi also generates an
        # (empty) 'application/json' schema in the OpenAPI spec, which confuses
        # the autorest tool. This here works even though the content isn't JSON.
        # See: https://github.com/Azure/autorest/blob/main/docs/openapi/howto/binary-payload.md
        fastapi.status.HTTP_200_OK: {
            "content": {
                "application/json": {"schema": {"type": "string", "format": "binary"}}
            }
        },
    },
    summary="Get the raw data for the Report.",
    response_description="A Parquet file containing the Report data.",
)
def reports_data(
    report_id: str,
    query_backend: QueryBackend = fastapi.Depends(get_query_backend),
    api_key: APIKey = fastapi.Depends(verify_api_key),
    endpoint: Endpoint = fastapi.Depends(get_endpoint),
):
    report = query_backend.get_report(report_id)
    if report is None:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
    check_endpoint_permissions_for_entity(api_key, endpoint, report)
    # FIXME: Handle multi-file data (or choose a better name than 'part-0')
    return _stream_from_storage(storage.paths.report_data(report_id))
