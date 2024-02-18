# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

"""
The request schemas describe the information that you need to provide when
creating new instances of the core types. For example, requests do not have
``.id`` fields because these are assigned by the platform when the resource
is created. Similarly, if a resource depends on an instance of another
resource, the request will refer to the dependency by its ID, while the core
resource will include the full dependency object as a sub-resource. The
``create`` endpoints take a request as input and return a full core resource
in response.
"""


from typing import Any, Optional, Union

import pydantic

from .base import DyffSchemaBaseModel
from .platform import (
    DatasetBase,
    DataView,
    EvaluationBase,
    InferenceServiceBase,
    InferenceSessionBase,
    Labeled,
    ModelSpec,
    ReportBase,
)
from .version import Versioned


class DyffEntityCreateRequest(Versioned, DyffSchemaBaseModel):
    account: str = pydantic.Field(description="Account that owns the entity")


class DatasetCreateRequest(DyffEntityCreateRequest, DatasetBase):
    pass


class ModelCreateRequest(DyffEntityCreateRequest, ModelSpec):
    pass


class InferenceServiceCreateRequest(DyffEntityCreateRequest, InferenceServiceBase):
    model: Optional[str] = pydantic.Field(
        default=None, description="ID of Model backing the service, if applicable"
    )


class InferenceSessionCreateRequest(DyffEntityCreateRequest, InferenceSessionBase):
    inferenceService: str = pydantic.Field(description="InferenceService ID")


class EvaluationInferenceSessionRequest(InferenceSessionBase):
    inferenceService: str = pydantic.Field(description="InferenceService ID")


class EvaluationCreateRequest(DyffEntityCreateRequest, EvaluationBase):
    """A description of how to run an InferenceService on a Dataset to obtain
    a set of evaluation results.
    """

    inferenceSession: EvaluationInferenceSessionRequest = pydantic.Field(
        description="Specification of the InferenceSession that will perform inference for the evaluation.",
    )


class ReportCreateRequest(DyffEntityCreateRequest, ReportBase):
    """A Report transforms raw model outputs into some useful statistics."""

    datasetView: Optional[Union[str, DataView]] = pydantic.Field(
        default=None,
        description="View of the input dataset required by the report (e.g., ground-truth labels).",
    )

    evaluationView: Optional[Union[str, DataView]] = pydantic.Field(
        default=None,
        description="View of the evaluation output data required by the report.",
    )


class LabelUpdateRequest(Labeled):
    pass


# Note: Query requests, as they currently exist, don't work with Versioned
# because fastapi will assign None to every field that the client doesn't
# specify. I think it's not that important, because all of the query parameters
# will always be optional. There could be a problem if the semantics of a
# name change, but let's just not do that!
class DyffEntityQueryRequest(DyffSchemaBaseModel):
    id: Optional[str] = pydantic.Field(default=None)
    account: Optional[str] = pydantic.Field(default=None)
    status: Optional[str] = pydantic.Field(default=None)
    reason: Optional[str] = pydantic.Field(default=None)
    labels: Optional[str] = pydantic.Field(
        default=None, description="Labels dict represented as a JSON string."
    )

    def dict(self, exclude_unset=True, **kwargs) -> dict[str, Any]:
        return super().dict(exclude_unset=exclude_unset, **kwargs)

    def json(self, exclude_unset=True, **kwargs) -> Any:
        return super().json(exclude_unset=exclude_unset, **kwargs)


class AuditQueryRequest(DyffEntityQueryRequest):
    name: Optional[str] = pydantic.Field(default=None)


class DatasetQueryRequest(DyffEntityQueryRequest):
    name: Optional[str] = pydantic.Field(default=None)


class EvaluationQueryRequest(DyffEntityQueryRequest):
    dataset: Optional[str] = pydantic.Field(default=None)
    inferenceService: Optional[str] = pydantic.Field(default=None)
    inferenceServiceName: Optional[str] = pydantic.Field(default=None)
    model: Optional[str] = pydantic.Field(default=None)
    modelName: Optional[str] = pydantic.Field(default=None)


class InferenceServiceQueryRequest(DyffEntityQueryRequest):
    name: Optional[str] = pydantic.Field(default=None)
    model: Optional[str] = pydantic.Field(default=None)
    modelName: Optional[str] = pydantic.Field(default=None)


class InferenceSessionQueryRequest(DyffEntityQueryRequest):
    name: Optional[str] = pydantic.Field(default=None)
    inferenceService: Optional[str] = pydantic.Field(default=None)
    inferenceServiceName: Optional[str] = pydantic.Field(default=None)
    model: Optional[str] = pydantic.Field(default=None)
    modelName: Optional[str] = pydantic.Field(default=None)


class ModelQueryRequest(DyffEntityQueryRequest):
    name: Optional[str] = pydantic.Field(default=None)


class ReportQueryRequest(DyffEntityQueryRequest):
    report: Optional[str] = pydantic.Field(default=None)
    dataset: Optional[str] = pydantic.Field(default=None)
    evaluation: Optional[str] = pydantic.Field(default=None)
    inferenceService: Optional[str] = pydantic.Field(default=None)
    model: Optional[str] = pydantic.Field(default=None)


__all__ = [
    "AuditQueryRequest",
    "DyffEntityCreateRequest",
    "DyffEntityQueryRequest",
    "DatasetCreateRequest",
    "DatasetQueryRequest",
    "EvaluationCreateRequest",
    "EvaluationQueryRequest",
    "EvaluationInferenceSessionRequest",
    "InferenceServiceCreateRequest",
    "InferenceServiceQueryRequest",
    "InferenceSessionCreateRequest",
    "InferenceSessionQueryRequest",
    "LabelUpdateRequest",
    "ModelCreateRequest",
    "ModelQueryRequest",
    "ReportCreateRequest",
    "ReportQueryRequest",
]
