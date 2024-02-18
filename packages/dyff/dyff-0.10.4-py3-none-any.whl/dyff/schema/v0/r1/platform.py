# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

"""Schema for the internal data representation of Dyff entities.

We use the following naming convention:

    * ``<Entity>``: A full-fledged entity that is tracked by the platform. It has
      an .id and the other dynamic system attributes like 'status'.
    * ``<Entity>Base``: The attributes of the Entity that are also attributes of
      the corresponding CreateRequest. Example: Number of replicas to use for
      an evaluation.
    * ``Foreign<Entity>``: Like <Entity>, but without dynamic system fields
      like 'status'. This type is used when we want to embed the full
      description of a resource inside of an outer resource that depends on it.
      We include the full dependency data structure so that downstream
      components don't need to be able to look it up by ID.
"""
# mypy: disable-error-code="import-untyped"
import abc
import enum
from datetime import datetime
from enum import Enum
from typing import Any, Literal, NamedTuple, Optional, Type, Union

import pyarrow
import pydantic
from typing_extensions import TypeAlias

from ... import named_data_schema, product_schema
from ...version import SomeSchemaVersion
from .base import DyffSchemaBaseModel
from .dataset import arrow, make_item_type, make_response_type
from .version import VERSION, Versioned

SYSTEM_ATTRIBUTES = frozenset(["creationTime", "status", "reason"])


def _k8s_quantity_regex():
    # This is copy-pasted from the regex that operator-sdk generates for resource.Quantity types
    return r"^(\+|-)?(([0-9]+(\.[0-9]*)?)|(\.[0-9]+))(([KMGTPE]i)|[numkMGTPE]|([eE](\+|-)?(([0-9]+(\.[0-9]*)?)|(\.[0-9]+))))?$"


def _k8s_label_regex():
    """A k8s label is like a DNS label but also allows ``.`` an ``_`` as
    separator characters.
    """
    return r"[a-z0-9A-Z]([-_.a-z0-9A-Z]{0,61}[a-z0-9A-Z])?"


def _k8s_label_maxlen():
    """Max length of a k8s label, same as for a DNS label."""
    return 63


def _dns_label_regex():
    """Alphanumeric characters separated by ``-``, maximum of 63 characters."""
    return r"[a-zA-Z0-9]([-a-zA-Z0-9]{0,61}[a-zA-Z0-9])?"


def _dns_label_maxlen():
    """Max length of a DNS label."""
    return 63


def _dns_domain_regex():
    """One or more DNS labels separated by dots (``.``). Note that its maximum
    length is 253 characters, but we can't enforce this in the regex.
    """
    return f"{_dns_label_regex()}(\.{_dns_label_regex()})*"


def _k8s_domain_maxlen():
    """Max length of a k8s domain. The DNS domain standard specifies 255
    characters, but this includes the trailing dot and null terminator. We
    never include a trailing dot in k8s-style domains.
    """
    return 253


def _k8s_label_key_regex():
    """The format of keys for labels and annotations. Optional subdomain prefix
    followed by a k8s label.

    See: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/

    Valid label keys have two segments: an optional prefix and name, separated
    by a slash (``/``). The name segment is required and must have 63 characters
    or fewer, consisting of alphanumeric characters separated by ``-``, ``.``,
    or ``_`` characters. The prefix is optional. If specified, it must be a
    DNS subdomain followed by a ``/`` character.

    Examples:

        * my-multi_segment.key
        * dyff.io/reserved-key
    """
    return f"^({_dns_domain_regex()}/)?{_dns_label_regex()}$"


def _k8s_label_key_maxlen():
    """Max length of a label key.

    The prefix segment, if present, has a max length of 253 characters. The
    name segment has a max length of 63 characters.

    See: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/
    """
    # subdomain + '/' + label
    # Note that the domain regex can't enforce its max length because it can
    # have an arbitrary number of parts (part1.part2...), but the label regex
    # *does* enforce a max length, so checking the overall length is sufficient
    # to limit the domain part to 253 characters.
    return _k8s_domain_maxlen() + 1 + _k8s_label_maxlen()


def _k8s_label_value_regex():
    """The format of values for labels.

    Label values must satisfy the following:

        * must have 63 characters or fewer (can be empty)
        * unless empty, must begin and end with an alphanumeric character (``[a-z0-9A-Z]``)
        * could contain dashes (``-``), underscores (``_``), dots (``.``), and alphanumerics between

    See: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/
    """
    return f"^({_k8s_label_regex()})?$"


def _k8s_label_value_maxlen():
    """Max length of a label value.

    Label values must have 63 characters or fewer (can be empty).

    See: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/
    """
    return _k8s_label_maxlen()


class StorageSignedURL(DyffSchemaBaseModel):
    url: str = pydantic.Field(description="The signed URL")
    method: str = pydantic.Field(description="The HTTP method applicable to the URL")
    headers: dict[str, str] = pydantic.Field(
        default_factory=dict,
        description="Mandatory headers that must be passed with the request",
    )


class Entities(str, enum.Enum):
    """The kinds of entities in the dyff system."""

    Account = "Account"
    Audit = "Audit"
    AuditProcedure = "AuditProcedure"
    DataSource = "DataSource"
    Dataset = "Dataset"
    Evaluation = "Evaluation"
    InferenceService = "InferenceService"
    InferenceSession = "InferenceSession"
    Model = "Model"
    Report = "Report"


class Resources(str, enum.Enum):
    """The resource names corresponding to entities that have API endpoints."""

    Audit = "audits"
    AuditProcedure = "auditprocedures"
    Dataset = "datasets"
    DataSource = "datasources"
    Evaluation = "evaluations"
    InferenceService = "inferenceservices"
    InferenceSession = "inferencesessions"
    Model = "models"
    Report = "reports"

    Task = "tasks"
    """
    .. deprecated:: 0.5.0

        The Task resource no longer exists, but removing this enum entry
        breaks existing API keys.
    """

    ALL = "*"

    @staticmethod
    def for_kind(kind: Entities) -> "Resources":
        if kind == Entities.Audit:
            return Resources.Audit
        elif kind == Entities.AuditProcedure:
            return Resources.AuditProcedure
        elif kind == Entities.Dataset:
            return Resources.Dataset
        elif kind == Entities.DataSource:
            return Resources.DataSource
        elif kind == Entities.Evaluation:
            return Resources.Evaluation
        elif kind == Entities.InferenceService:
            return Resources.InferenceService
        elif kind == Entities.InferenceSession:
            return Resources.InferenceSession
        elif kind == Entities.Model:
            return Resources.Model
        elif kind == Entities.Report:
            return Resources.Report
        else:
            raise ValueError(f"No Resources for Entity kind: {kind}")


class DyffModelWithID(DyffSchemaBaseModel):
    id: str = pydantic.Field(description="Unique identifier of the entity")
    account: str = pydantic.Field(description="Account that owns the entity")


LabelKey: TypeAlias = pydantic.constr(  # type: ignore
    regex=_k8s_label_key_regex(), max_length=_k8s_label_key_maxlen()
)


LabelValue: TypeAlias = Optional[  # type: ignore
    pydantic.constr(
        regex=_k8s_label_value_regex(), max_length=_k8s_label_value_maxlen()
    )
]


class Label(DyffSchemaBaseModel):
    """A key-value label for a resource. Used to specify identifying attributes
    of resources that are meaningful to users but do not imply semantics in the
    dyff system.

    We follow the kubernetes label conventions closely. See:
    https://kubernetes.io/docs/concepts/overview/working-with-objects/labels
    """

    key: LabelKey = pydantic.Field(
        description="The label key is a DNS label with an optional DNS domain"
        " prefix. For example: 'my-key', 'your.com/key_0'. Keys prefixed with"
        " 'dyff.io/', 'subdomain.dyff.io/', etc. are reserved.",
    )

    value: LabelValue = pydantic.Field(
        description="The label value consists of alphanumeric characters"
        " separated by '.', '-', or '_'.",
    )


class Labeled(DyffSchemaBaseModel):
    labels: dict[LabelKey, LabelValue] = pydantic.Field(
        default_factory=dict,
        description="A set of key-value labels for the resource. Used to"
        " specify identifying attributes of resources that are meaningful to"
        " users but do not imply semantics in the dyff system.\n\n"
        "The keys are DNS labels with an optional DNS domain prefix."
        " For example: 'my-key', 'your.com/key_0'. Keys prefixed with"
        " 'dyff.io/', 'subdomain.dyff.io/', etc. are reserved.\n\n"
        "The label values are alphanumeric characters separated by"
        " '.', '-', or '_'.\n\n"
        "We follow the kubernetes label conventions closely."
        " See: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels",
    )


class Annotation(DyffSchemaBaseModel):
    key: str = pydantic.Field(
        regex=_k8s_label_key_regex(),
        max_length=_k8s_domain_maxlen(),
        description="The annotation key. A DNS label with an optional DNS domain prefix."
        " For example: 'my-key', 'your.com/key_0'. Names prefixed with"
        " 'dyff.io/', 'subdomain.dyff.io/', etc. are reserved.\n\n"
        "See https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations"
        " for detailed naming rules.",
    )

    value: str = pydantic.Field(
        description="The annotation value. An arbitrary string."
    )


Quantity: TypeAlias = pydantic.constr(regex=_k8s_quantity_regex())  # type: ignore


class ServiceClass(str, enum.Enum):
    """Defines the "quality of service" characteristics of a resource
    allocation.
    """

    STANDARD = "standard"
    PREEMPTIBLE = "preemptible"


class ResourceAllocation(DyffSchemaBaseModel):
    quantities: dict[LabelKey, Quantity] = pydantic.Field(
        default_factory=dict,
        description="Mapping of resource keys to quantities to be allocated.",
    )

    serviceClass: ServiceClass = pydantic.Field(description="The service class")


class Status(DyffSchemaBaseModel):
    status: str = pydantic.Field(
        default=None, description="Top-level resource status (assigned by system)"
    )

    reason: Optional[str] = pydantic.Field(
        default=None, description="Reason for current status (assigned by system)"
    )


class DyffEntity(Status, Labeled, Versioned, DyffModelWithID):
    kind: Literal[
        "Audit",
        "AuditProcedure",
        "DataSource",
        "Dataset",
        "Evaluation",
        "InferenceService",
        "InferenceSession",
        "Model",
        "Report",
    ]

    annotations: list[Annotation] = pydantic.Field(
        default_factory=list,
        description="A set of key-value annotations for the resource. Used to"
        " attach arbitrary non-identifying metadata to resources."
        " We follow the kubernetes annotation conventions closely.\n\n"
        " See: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations",
    )

    creationTime: datetime = pydantic.Field(
        default=None, description="Resource creation time (assigned by system)"
    )

    @abc.abstractmethod
    def dependencies(self) -> list[str]:
        """List of IDs of resources that this resource depends on.

        The workflow cannot start until all dependencies have reached a success
        status. Workflows waiting for dependencies have
        ``reason = UnsatisfiedDependency``. If any dependency reaches a failure
        status, this workflow will also fail with ``reason = FailedDependency``.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def resource_allocation(self) -> Optional[ResourceAllocation]:
        """Resource allocation required to run this workflow, if any."""
        raise NotImplementedError()


class Frameworks(str, enum.Enum):
    transformers = "transformers"


class InferenceServiceSources(str, enum.Enum):
    upload = "upload"
    build = "build"


class APIFunctions(str, enum.Enum):
    """Categories of API operations to which access can be granted."""

    consume = "consume"
    """Use the resource as a dependency in another workflow.

    Example: running an ``Evaluation`` on a ``Dataset`` requires ``consume``
    permission for the ``Dataset``.
    """

    create = "create"
    """Create a new instance of the resource.

    For resources that require uploading artifacts (such as ``Dataset``), also
    grants access to the ``upload`` and ``finalize`` endpoints.
    """

    get = "get"
    """Retrieve a single resource instance by ID."""

    query = "query"
    """Query the resource collection."""

    download = "download"
    """
    .. deprecated:: 0.5.0

        This functionality has been consolidated into ``data``.
    """

    upload = "upload"
    """
    .. deprecated:: 0.5.0

        This functionality has been consolidated into ``create``.
    """

    data = "data"
    """Download the raw data associated with the resource."""

    strata = "strata"
    """
    .. deprecated:: 0.5.0

        Similar functionality will be added in the future but with a different
        interface.
    """

    terminate = "terminate"
    """Set the resource status to ``Terminated``."""

    delete = "delete"
    """Set the resource status to ``Deleted``."""

    all = "*"


class AccessGrant(DyffSchemaBaseModel):
    """Grants access to call particular functions on particular instances of
    particular resource types.

    Access grants are **additive**; the subject of a set of grants has
    permission to do something if any part of any of those grants gives the
    subject that permission.
    """

    resources: list[Resources] = pydantic.Field(
        min_items=1, description="List of resource types to which the grant applies"
    )
    functions: list[APIFunctions] = pydantic.Field(
        min_items=1,
        description="List of functions on those resources to which the grant applies",
    )
    accounts: list[str] = pydantic.Field(
        default_factory=list,
        description="The access grant applies to all resources owned by the listed accounts",
    )
    entities: list[str] = pydantic.Field(
        default_factory=list,
        description="The access grant applies to all resources with IDs listed in 'entities'",
    )


class APIKey(DyffSchemaBaseModel):
    """A description of a set of permissions granted to a single subject
    (either an account or a workload).

    Dyff API clients authenticate with a *token* that contains a
    cryptographically signed APIKey.
    """

    id: str = pydantic.Field(
        description="Unique ID of the resource. Maps to JWT 'jti' claim."
    )
    # TODO: Needs validator
    subject: str = pydantic.Field(
        description="Subject of access grants ('<kind>/<id>'). Maps to JWT 'sub' claim."
    )
    created: datetime = pydantic.Field(
        description="When the APIKey was created. Maps to JWT 'iat' claim."
    )
    expires: datetime = pydantic.Field(
        description="When the APIKey expires. Maps to JWT 'exp' claim."
    )
    secret: Optional[str] = pydantic.Field(
        default=None,
        description="For account keys: a secret value to check when verifying the APIKey",
    )
    grants: list[AccessGrant] = pydantic.Field(
        default_factory=list, description="AccessGrants associated with the APIKey"
    )


class AuditRequirement(DyffSchemaBaseModel):
    """An evaluation report that must exist in order to apply an AuditProcedure."""

    dataset: str
    rubric: str


class AuditProcedure(DyffEntity):
    """An audit procedure that can be run against a set of evaluation reports."""

    kind: Literal["AuditProcedure"] = Entities.AuditProcedure.value

    name: str
    requirements: list[AuditRequirement] = pydantic.Field(default_factory=list)

    def dependencies(self) -> list[str]:
        # Note that ``requirements`` are not "dependencies" because they don't
        # refer to a specific entity
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class Audit(DyffEntity):
    """An instance of applying an AuditProcedure to an InferenceService."""

    kind: Literal["Audit"] = Entities.Audit.value

    auditProcedure: str = pydantic.Field(description="The AuditProcedure to run.")

    inferenceService: str = pydantic.Field(description="The InferenceService to audit.")

    def dependencies(self) -> list[str]:
        return [self.auditProcedure, self.inferenceService]

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class DataSource(DyffEntity):
    """A source of raw data from which a Dataset can be built."""

    kind: Literal["DataSource"] = Entities.DataSource.value

    name: str
    sourceKind: str
    source: Optional[str] = None

    def dependencies(self) -> list[str]:
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class ArchiveFormat(DyffSchemaBaseModel):
    """Specification of the archives that comprise a DataSource."""

    name: str
    format: str


class ExtractorStep(DyffSchemaBaseModel):
    """Description of a step in the process of turning a hierarchical
    DataSource into a Dataset.
    """

    action: str
    name: Optional[str] = None
    type: Optional[str] = None


class Digest(DyffSchemaBaseModel):
    md5: Optional[str] = pydantic.Field(None)


class Artifact(DyffSchemaBaseModel):
    # TODO: Enumerate the available kinds
    kind: str = pydantic.Field(description="The kind of artifact")
    path: str = pydantic.Field(
        description="The relative path of the artifact within the dataset"
    )
    digest: Digest = pydantic.Field(
        description="One or more message digests (hashes) of the artifact data"
    )


class DyffDataSchema(DyffSchemaBaseModel):
    components: list[str] = pydantic.Field(
        min_items=1,
        description="A list of named dyff data schemas. The final schema is"
        " the composition of these component schemas.",
    )
    schemaVersion: SomeSchemaVersion = pydantic.Field(
        default=VERSION, description="The dyff schema version"
    )

    def model_type(self) -> Type[DyffSchemaBaseModel]:
        """The composite model type."""
        return product_schema(
            named_data_schema(c, self.schemaVersion) for c in self.components
        )


class DataSchema(DyffSchemaBaseModel):
    arrowSchema: str = pydantic.Field(
        description="The schema in Arrow format, encoded with"
        " dyff.schema.arrow.encode_schema(). This is required, but can be"
        " populated from a DyffDataSchema.",
    )
    dyffSchema: Optional[DyffDataSchema] = pydantic.Field(
        default=None, description="The schema in DyffDataSchema format"
    )
    jsonSchema: Optional[dict[str, Any]] = pydantic.Field(
        default=None, description="The schema in JSON Schema format"
    )

    @staticmethod
    def make_input_schema(
        schema: Union[pyarrow.Schema, Type[DyffSchemaBaseModel], DyffDataSchema],
    ) -> "DataSchema":
        """Construct a complete ``DataSchema`` for inference inputs.

        This function will add required special fields for input data and then
        convert the augmented schema as necessary to populate at least the
        required ``arrowSchema`` field in the resulting ``DataSchema``.
        """
        if isinstance(schema, pyarrow.Schema):
            arrowSchema = arrow.encode_schema(arrow.make_item_schema(schema))
            return DataSchema(arrowSchema=arrowSchema)
        elif isinstance(schema, DyffDataSchema):
            item_model = make_item_type(schema.model_type())
            arrowSchema = arrow.encode_schema(arrow.arrow_schema(item_model))
            jsonSchema = item_model.schema()
            return DataSchema(
                arrowSchema=arrowSchema, dyffSchema=schema, jsonSchema=jsonSchema
            )
        else:
            item_model = make_item_type(schema)
            arrowSchema = arrow.encode_schema(arrow.arrow_schema(item_model))
            jsonSchema = item_model.schema()
            return DataSchema(arrowSchema=arrowSchema, jsonSchema=jsonSchema)

    @staticmethod
    def make_output_schema(
        schema: Union[pyarrow.Schema, Type[DyffSchemaBaseModel], DyffDataSchema],
    ) -> "DataSchema":
        """Construct a complete ``DataSchema`` for inference inputs.

        This function will add required special fields for input data and then
        convert the augmented schema as necessary to populate at least the
        required ``arrowSchema`` field in the resulting ``DataSchema``.
        """
        if isinstance(schema, pyarrow.Schema):
            arrowSchema = arrow.encode_schema(arrow.make_response_schema(schema))
            return DataSchema(arrowSchema=arrowSchema)
        elif isinstance(schema, DyffDataSchema):
            response_model = make_response_type(schema.model_type())
            arrowSchema = arrow.encode_schema(arrow.arrow_schema(response_model))
            jsonSchema = response_model.schema()
            return DataSchema(
                arrowSchema=arrowSchema, dyffSchema=schema, jsonSchema=jsonSchema
            )
        else:
            response_model = make_response_type(schema)
            arrowSchema = arrow.encode_schema(arrow.arrow_schema(response_model))
            jsonSchema = response_model.schema()
            return DataSchema(arrowSchema=arrowSchema, jsonSchema=jsonSchema)


class SchemaAdapter(DyffSchemaBaseModel):
    kind: str = pydantic.Field(
        description="Name of a schema adapter available on the platform",
    )

    configuration: Optional[dict[str, Any]] = pydantic.Field(
        default=None,
        description="Configuration for the schema adapter. Must be encodable as JSON.",
    )


class DataView(DyffSchemaBaseModel):
    id: str = pydantic.Field(description="Unique ID of the DataView")
    viewOf: str = pydantic.Field(
        description="ID of the resource that this is a view of"
    )
    schema_: DataSchema = pydantic.Field(
        alias="schema", description="Schema of the output of this view"
    )
    adapterPipeline: Optional[list[SchemaAdapter]] = pydantic.Field(
        default=None, description="Adapter pipeline to apply to produce the view"
    )


class DatasetBase(DyffSchemaBaseModel):
    name: str = pydantic.Field(description="The name of the Dataset")
    artifacts: list[Artifact] = pydantic.Field(
        min_items=1, description="Artifacts that comprise the dataset"
    )
    schema_: DataSchema = pydantic.Field(
        alias="schema", description="Schema of the dataset"
    )
    views: list[DataView] = pydantic.Field(
        default_factory=list,
        description="Available views of the data that alter its schema.",
    )


class Dataset(DyffEntity, DatasetBase):
    """An "ingested" data set in our standardized PyArrow format."""

    kind: Literal["Dataset"] = Entities.Dataset.value

    def dependencies(self) -> list[str]:
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class ModelSourceKinds(str, enum.Enum):
    GitLFS = "GitLFS"
    HuggingFaceHub = "HuggingFaceHub"
    OpenLLM = "OpenLLM"
    Upload = "Upload"


class ModelSourceGitLFS(DyffSchemaBaseModel):
    url: pydantic.HttpUrl = pydantic.Field(
        description="The URL of the Git LFS repository"
    )


class ModelSourceHuggingFaceHub(DyffSchemaBaseModel):
    """These arguments are forwarded to huggingface_hub.snapshot_download()"""

    repoID: str
    revision: str
    allowPatterns: Optional[list[str]] = None
    ignorePatterns: Optional[list[str]] = None


class ModelSourceOpenLLM(DyffSchemaBaseModel):
    modelKind: str = pydantic.Field(
        description="The kind of model (c.f. 'openllm build <modelKind>')"
    )

    modelID: str = pydantic.Field(
        description="The specific model identifier (c.f. 'openllm build ... --model-id <modelId>')",
    )

    modelVersion: str = pydantic.Field(
        description="The version of the model (e.g., a git commit hash)"
    )


class ModelSource(DyffSchemaBaseModel):
    kind: ModelSourceKinds = pydantic.Field(description="The kind of model source")

    gitLFS: Optional[ModelSourceGitLFS] = pydantic.Field(
        default=None, description="Specification of a Git LFS source"
    )

    huggingFaceHub: Optional[ModelSourceHuggingFaceHub] = pydantic.Field(
        default=None, description="Specification of a HuggingFace Hub source"
    )

    openLLM: Optional[ModelSourceOpenLLM] = pydantic.Field(
        default=None, description="Specification of an OpenLLM source"
    )


class AcceleratorGPU(DyffSchemaBaseModel):
    hardwareTypes: list[str] = pydantic.Field(
        min_items=1,
        description="Acceptable GPU hardware types.",
    )
    count: int = pydantic.Field(default=1, description="Number of GPUs required.")
    memory: Optional[Quantity] = pydantic.Field(
        default=None,
        description="[DEPRECATED] Amount of GPU memory required, in k8s Quantity notation",
    )


class Accelerator(DyffSchemaBaseModel):
    kind: str = pydantic.Field(
        description="The kind of accelerator; available kinds are {{GPU}}"
    )
    gpu: Optional[AcceleratorGPU] = pydantic.Field(
        default=None, description="GPU accelerator options"
    )


class ModelResources(DyffSchemaBaseModel):
    storage: Quantity = pydantic.Field(
        description="Amount of storage required for packaged model, in k8s Quantity notation",
    )

    memory: Optional[Quantity] = pydantic.Field(
        default=None,
        description="Amount of memory required to run the model on CPU, in k8s Quantity notation",
    )


class ModelStorageMedium(str, enum.Enum):
    ObjectStorage = "ObjectStorage"
    PersistentVolume = "PersistentVolume"


class ModelArtifactKind(str, enum.Enum):
    HuggingFaceCache = "HuggingFaceCache"


class ModelArtifactHuggingFaceCache(DyffSchemaBaseModel):
    repoID: str = pydantic.Field(
        description="Name of the model in the HuggingFace cache"
    )
    revision: str = pydantic.Field(description="Model revision")

    def snapshot_path(self) -> str:
        return f"models--{self.repoID.replace('/', '--')}/snapshots/{self.revision}"


class ModelArtifact(DyffSchemaBaseModel):
    kind: ModelArtifactKind = pydantic.Field(
        description="How the model data is represented"
    )
    huggingFaceCache: Optional[ModelArtifactHuggingFaceCache] = pydantic.Field(
        description="Model stored in a HuggingFace cache"
    )


class ModelStorage(DyffSchemaBaseModel):
    medium: ModelStorageMedium = pydantic.Field(description="Storage medium")


class ModelBase(DyffSchemaBaseModel):
    name: str = pydantic.Field(description="The name of the Model.")

    artifact: ModelArtifact = pydantic.Field(
        description="How the model data is represented"
    )

    storage: ModelStorage = pydantic.Field(description="How the model data is stored")


class ModelSpec(ModelBase):
    source: ModelSource = pydantic.Field(
        description="Source from which the model artifact was obtained"
    )

    resources: ModelResources = pydantic.Field(
        description="Resource requirements of the model."
    )

    accelerators: Optional[list[Accelerator]] = pydantic.Field(
        default=None,
        description="Accelerator hardware that is compatible with the model.",
    )


class Model(DyffEntity, ModelSpec):
    """A Model is the "raw" form of an inference model, from which one or more
    InferenceServices may be built.
    """

    kind: Literal["Model"] = Entities.Model.value

    def dependencies(self) -> list[str]:
        return []

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class InferenceServiceBuilder(DyffSchemaBaseModel):
    kind: str
    args: Optional[list[str]] = None


class InferenceServiceRunnerKind(str, Enum):
    BENTOML_SERVICE_OPENLLM = "bentoml_service_openllm"
    HUGGINGFACE = "huggingface"
    MOCK = "mock"
    STANDALONE = "standalone"
    VLLM = "vllm"


class InferenceServiceRunner(DyffSchemaBaseModel):
    kind: InferenceServiceRunnerKind
    args: Optional[list[str]] = pydantic.Field(
        default=None, description="Command line arguments to forward to the runner"
    )

    accelerator: Optional[Accelerator] = pydantic.Field(
        default=None, description="Optional accelerator hardware to use"
    )

    resources: ModelResources = pydantic.Field(
        description="Resource requirements to run the service."
    )


class InferenceInterface(DyffSchemaBaseModel):
    endpoint: str = pydantic.Field(description="HTTP endpoint for inference.")

    outputSchema: DataSchema = pydantic.Field(
        description="Schema of the inference outputs.",
    )

    inputPipeline: Optional[list[SchemaAdapter]] = pydantic.Field(
        default=None, description="Input adapter pipeline."
    )

    outputPipeline: Optional[list[SchemaAdapter]] = pydantic.Field(
        default=None, description="Output adapter pipeline."
    )


class ForeignModel(DyffModelWithID, ModelBase):
    pass


class InferenceServiceBase(DyffSchemaBaseModel):
    name: str = pydantic.Field(description="The name of the service.")

    builder: Optional[InferenceServiceBuilder] = pydantic.Field(
        default=None,
        description="Configuration of the Builder used to build the service.",
    )

    runner: Optional[InferenceServiceRunner] = pydantic.Field(
        default=None, description="Configuration of the Runner used to run the service."
    )

    interface: InferenceInterface = pydantic.Field(
        description="How to move data in and out of the service."
    )

    outputViews: list[DataView] = pydantic.Field(
        default_factory=list,
        description="Views of the output data for different purposes.",
    )


class InferenceServiceSpec(InferenceServiceBase):
    model: Optional[ForeignModel] = pydantic.Field(
        default=None,
        description="The Model backing this InferenceService, if applicable.",
    )


class InferenceService(DyffEntity, InferenceServiceSpec):
    """An InferenceService is an inference model packaged as a Web service."""

    kind: Literal["InferenceService"] = Entities.InferenceService.value

    def dependencies(self) -> list[str]:
        result = []
        if self.model is not None:
            result.append(self.model.id)
        return result

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class ForeignInferenceService(DyffModelWithID, InferenceServiceSpec):
    pass


class InferenceSessionBase(DyffSchemaBaseModel):
    expires: Optional[datetime] = pydantic.Field(
        default=None,
        description="Expiration time for the session. Use of this field is recommended to avoid accidental compute costs.",
    )

    replicas: int = pydantic.Field(default=1, description="Number of model replicas")

    accelerator: Optional[Accelerator] = pydantic.Field(
        default=None, description="Accelerator hardware to use."
    )

    useSpotPods: bool = pydantic.Field(
        default=True, description="Use 'spot pods' for cheaper computation"
    )


class InferenceSessionSpec(InferenceSessionBase):
    inferenceService: ForeignInferenceService = pydantic.Field(
        description="InferenceService ID"
    )


class InferenceSession(DyffEntity, InferenceSessionSpec):
    """An InferenceSession is a deployment of an InferenceService that exposes
    an API for interactive queries.
    """

    kind: Literal["InferenceSession"] = Entities.InferenceSession.value

    def dependencies(self) -> list[str]:
        return [self.inferenceService.id]

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class InferenceSessionAndToken(DyffSchemaBaseModel):
    inferencesession: InferenceSession
    token: str


class DatasetFilter(DyffSchemaBaseModel):
    """A rule for restrcting which instances in a Dataset are returned."""

    field: str
    relation: str
    value: str


class TaskSchema(DyffSchemaBaseModel):
    # InferenceServices must consume a *subset* of this schema
    input: DataSchema
    # InferenceServices must output a *superset* of this schema
    output: DataSchema
    # This will be an enumerated tag specifying task semantics (e.g., Classification, TextGeneration)
    objective: str


class EvaluationBase(DyffSchemaBaseModel):
    dataset: str = pydantic.Field(description="The Dataset to evaluate on.")

    replications: int = pydantic.Field(
        default=1, description="Number of replications to run."
    )

    workersPerReplica: Optional[int] = pydantic.Field(
        default=None,
        description="Number of data workers per inference service replica.",
    )


class Evaluation(DyffEntity, EvaluationBase):
    """A description of how to run an InferenceService on a Dataset to obtain
    a set of evaluation results.
    """

    kind: Literal["Evaluation"] = Entities.Evaluation.value

    inferenceSession: InferenceSessionSpec = pydantic.Field(
        description="Specification of the InferenceSession that will perform inference for the evaluation.",
    )

    def dependencies(self) -> list[str]:
        return [self.dataset, self.inferenceSession.inferenceService.id]

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


class ReportBase(DyffSchemaBaseModel):
    rubric: str = pydantic.Field(
        description="The scoring rubric to apply (e.g., 'classification.TopKAccuracy').",
    )

    evaluation: str = pydantic.Field(
        description="The evaluation (and corresponding output data) to run the report on."
    )


class Report(DyffEntity, ReportBase):
    """A Report transforms raw model outputs into some useful statistics."""

    kind: Literal["Report"] = Entities.Report.value

    dataset: str = pydantic.Field(description="The input dataset.")

    inferenceService: str = pydantic.Field(
        description="The inference service used in the evaluation"
    )

    model: Optional[str] = pydantic.Field(
        default=None,
        description="The model backing the inference service, if applicable",
    )

    datasetView: Optional[DataView] = pydantic.Field(
        default=None,
        description="View of the input dataset required by the report (e.g., ground-truth labels).",
    )

    evaluationView: Optional[DataView] = pydantic.Field(
        default=None,
        description="View of the evaluation output data required by the report.",
    )

    def dependencies(self) -> list[str]:
        return [self.evaluation]

    def resource_allocation(self) -> Optional[ResourceAllocation]:
        return None


# ---------------------------------------------------------------------------
# Status enumerations


class _JobStatus(NamedTuple):
    """The set of basic ``status`` values that are applicable to all "job"
    entities (entities that involve computation tasks).
    """

    complete: str = "Complete"
    failed: str = "Failed"


JobStatus = _JobStatus()


class _ResourceStatus(NamedTuple):
    """The set of basic ``status`` values that are applicable to all "resource"
    entities.
    """

    ready: str = "Ready"
    error: str = "Error"


ResourceStatus = _ResourceStatus()


class _EntityStatus(NamedTuple):
    """The set of basic ``status`` values that are applicable to most entity types."""

    created: str = "Created"
    schedulable: str = "Schedulable"
    admitted: str = "Admitted"
    terminated: str = "Terminated"
    deleted: str = "Deleted"
    ready: str = ResourceStatus.ready
    complete: str = JobStatus.complete
    error: str = ResourceStatus.error
    failed: str = JobStatus.failed


EntityStatus = _EntityStatus()


class _EntityStatusReason(NamedTuple):
    """The set of basic ``reason`` values that are applicable to most entity types."""

    quota_limit: str = "QuotaLimit"
    unsatisfied_dependency: str = "UnsatisfiedDependency"
    failed_dependency: str = "FailedDependency"
    terminate_command: str = "TerminateCommand"
    delete_command: str = "DeleteCommand"
    expired: str = "Expired"


EntityStatusReason = _EntityStatusReason()


class _AuditStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``Audit`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    complete: str = EntityStatus.complete
    failed: str = EntityStatus.failed


AuditStatus = _AuditStatus()


class _DataSources(NamedTuple):
    huggingface: str = "huggingface"
    upload: str = "upload"
    zenodo: str = "zenodo"


DataSources = _DataSources()


class _DataSourceStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``DataSource`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    ready: str = EntityStatus.ready
    error: str = EntityStatus.error


DataSourceStatus = _DataSourceStatus()


class _DataSourceStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``DataSource`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    fetch_failed: str = "FetchFailed"
    upload_failed: str = "UploadFailed"


DataSourceStatusReason = _DataSourceStatusReason()


class _DatasetStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``Dataset`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    ready: str = EntityStatus.ready
    error: str = EntityStatus.error


DatasetStatus = _DatasetStatus()


class _DatasetStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``Dataset`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    data_source_missing: str = "DataSourceMissing"
    ingest_failed: str = "IngestFailed"
    waiting_for_data_source: str = "WaitingForDataSource"


DatasetStatusReason = _DatasetStatusReason()


class _EvaluationStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``Evaluation`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    complete: str = EntityStatus.complete
    failed: str = EntityStatus.failed


EvaluationStatus = _EvaluationStatus()


class _EvaluationStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``Evaluation`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    incomplete: str = "Incomplete"
    unverified: str = "Unverified"
    restarted: str = "Restarted"


EvaluationStatusReason = _EvaluationStatusReason()


class _ModelStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``Model`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    ready: str = EntityStatus.ready
    error: str = EntityStatus.error


ModelStatus = _ModelStatus()


class _ModelStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``Model`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    fetch_failed: str = "FetchFailed"


ModelStatusReason = _ModelStatusReason()


class _InferenceServiceStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``InferenceService`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    ready: str = EntityStatus.ready
    error: str = EntityStatus.error


InferenceServiceStatus = _InferenceServiceStatus()


class _InferenceServiceStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``InferenceService`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    build_failed: str = "BuildFailed"
    no_such_model: str = "NoSuchModel"
    waiting_for_model: str = "WaitingForModel"


InferenceServiceStatusReason = _InferenceServiceStatusReason()


class _ReportStatus(NamedTuple):
    """The set of ``status`` values that are applicable to ``Report`` entities."""

    created: str = EntityStatus.created
    admitted: str = EntityStatus.admitted
    complete: str = EntityStatus.complete
    failed: str = EntityStatus.failed


ReportStatus = _ReportStatus()


class _ReportStatusReason(NamedTuple):
    """The set of ``reason`` values that are applicable to ``Report`` entities."""

    quota_limit: str = EntityStatusReason.quota_limit
    no_such_evaluation: str = "NoSuchEvaluation"
    waiting_for_evaluation: str = "WaitingForEvaluation"


ReportStatusReason = _ReportStatusReason()


def is_status_terminal(status: str) -> bool:
    return status in [
        EntityStatus.complete,
        EntityStatus.error,
        EntityStatus.failed,
        EntityStatus.ready,
        EntityStatus.terminated,
        EntityStatus.deleted,
    ]


def is_status_failure(status: str) -> bool:
    return status in [EntityStatus.error, EntityStatus.failed]


def is_status_success(status: str) -> bool:
    return status in [EntityStatus.complete, EntityStatus.ready]


_ENTITY_CLASS = {
    Entities.Audit: Audit,
    Entities.AuditProcedure: AuditProcedure,
    Entities.Dataset: Dataset,
    Entities.DataSource: DataSource,
    Entities.Evaluation: Evaluation,
    Entities.InferenceService: InferenceService,
    Entities.InferenceSession: InferenceSession,
    Entities.Model: Model,
    Entities.Report: Report,
}


def entity_class(kind: Entities):
    return _ENTITY_CLASS[kind]


DyffEntityType = Union[
    Audit,
    AuditProcedure,
    DataSource,
    Dataset,
    Evaluation,
    InferenceService,
    InferenceSession,
    Model,
    Report,
]


__all__ = [
    "Accelerator",
    "AcceleratorGPU",
    "AccessGrant",
    "Annotation",
    "APIFunctions",
    "APIKey",
    "ArchiveFormat",
    "Artifact",
    "Audit",
    "AuditProcedure",
    "AuditRequirement",
    "DataSchema",
    "Dataset",
    "DatasetBase",
    "DatasetFilter",
    "DataSource",
    "DataSources",
    "DataView",
    "Digest",
    "DyffDataSchema",
    "DyffEntity",
    "DyffModelWithID",
    "DyffSchemaBaseModel",
    "Entities",
    "Evaluation",
    "EvaluationBase",
    "ExtractorStep",
    "ForeignInferenceService",
    "ForeignModel",
    "Frameworks",
    "InferenceInterface",
    "InferenceService",
    "InferenceServiceBase",
    "InferenceServiceBuilder",
    "InferenceServiceRunner",
    "InferenceServiceRunnerKind",
    "InferenceServiceSources",
    "InferenceServiceSpec",
    "InferenceSession",
    "InferenceSessionAndToken",
    "InferenceSessionBase",
    "InferenceSessionSpec",
    "Label",
    "LabelKey",
    "LabelValue",
    "Labeled",
    "Model",
    "ModelArtifact",
    "ModelArtifactHuggingFaceCache",
    "ModelArtifactKind",
    "ModelBase",
    "ModelStorageMedium",
    "ModelResources",
    "ModelSource",
    "ModelSourceGitLFS",
    "ModelSourceHuggingFaceHub",
    "ModelSourceKinds",
    "ModelSourceOpenLLM",
    "ModelSpec",
    "ModelStorage",
    "Report",
    "ReportBase",
    "Resources",
    "SchemaAdapter",
    "Status",
    "StorageSignedURL",
    "TaskSchema",
    "entity_class",
    "JobStatus",
    "EntityStatus",
    "EntityStatusReason",
    "AuditStatus",
    "DataSourceStatus",
    "DatasetStatus",
    "DatasetStatusReason",
    "EvaluationStatus",
    "EvaluationStatusReason",
    "InferenceServiceStatus",
    "InferenceServiceStatusReason",
    "ModelStatus",
    "ModelStatusReason",
    "ReportStatus",
    "ReportStatusReason",
    "is_status_terminal",
    "is_status_failure",
    "is_status_success",
    "DyffEntityType",
    "SYSTEM_ATTRIBUTES",
]
