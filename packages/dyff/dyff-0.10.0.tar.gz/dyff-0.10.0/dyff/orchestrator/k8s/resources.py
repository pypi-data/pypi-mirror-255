# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
from __future__ import annotations

import datetime
import enum
from functools import singledispatch
from typing import Any

import kubernetes as k8s

from dyff.schema.base import DyffSchemaBaseModel

from ...api import timestamp
from ...api.typing import YAMLList, YAMLObject, YAMLScalar, YAMLType
from ...schema.platform import (
    SYSTEM_ATTRIBUTES,
    Dataset,
    Entities,
    Evaluation,
    InferenceService,
    InferenceSession,
    Model,
    Report,
    Resources,
)

_DYFF_GROUP = "dyff.io"
_DYFF_VERSION = "v1alpha1"
_DYFF_API_VERSION = f"{_DYFF_GROUP}/{_DYFF_VERSION}"


@singledispatch
def to_yaml(spec: Any) -> YAMLType:
    if spec is None:
        return None
    else:
        raise TypeError(f"No conversion defined for {type(spec)}")


@to_yaml.register
def _(spec: datetime.datetime) -> str:
    return timestamp.dt_to_str(spec)


@to_yaml.register
def _(spec: enum.Enum) -> YAMLType:
    return spec.name


@to_yaml.register(str)
def _(spec) -> YAMLScalar:
    # If type uses the Subclass(str, Enum) pattern, singledispatch will detect
    # it as a str.
    if isinstance(spec, enum.Enum):
        return spec.name
    else:
        return spec


@to_yaml.register(int)
@to_yaml.register(float)
@to_yaml.register(bool)
def _(spec) -> YAMLScalar:
    return spec


@to_yaml.register
def _(spec: dict) -> YAMLObject:
    return {k: to_yaml(v) for k, v in spec.items()}


@to_yaml.register
def _(spec: list) -> YAMLList:
    return [to_yaml(x) for x in spec]


@to_yaml.register(Dataset)
@to_yaml.register(Evaluation)
@to_yaml.register(InferenceService)
@to_yaml.register(InferenceSession)
@to_yaml.register(Model)
@to_yaml.register(Report)
def _(spec: DyffSchemaBaseModel) -> YAMLObject:
    d = spec.dict()
    for k in SYSTEM_ATTRIBUTES:
        d.pop(k, None)
    return to_yaml(d)  # type: ignore


_short_names = {
    Entities.Audit: "audit",
    Entities.Dataset: "data",
    Entities.Evaluation: "eval",
    Entities.InferenceService: "infer",
    Entities.InferenceSession: "session",
    Entities.Model: "model",
    Entities.Report: "report",
}


_component_names = {
    Entities.Audit: {"fetch": "fetch", "proxy": "proxy", "run": "run"},
    Entities.Dataset: {
        "ingest": "ingest",
    },
    Entities.Evaluation: {
        "client": "client",
        "inference": "infer",
        "verification": "verify",
    },
    Entities.InferenceService: {
        "build": "build",
    },
    Entities.InferenceSession: {
        "inference": "infer",
    },
    Entities.Model: {
        "fetch": "fetch",
    },
    Entities.Report: {
        "run": "run",
    },
}


def object_name(kind: Entities | str, id: str, component=None) -> str:
    kind = Entities(kind)
    short_name = _short_names[kind]
    if component:
        component_name = _component_names[kind][component]
        return f"{short_name}-{id}-{component_name}"
    else:
        return f"{short_name}-{id}"


def evaluation_name(id: str, component=None) -> str:
    """Returns the k8s name of an evaluation-related component.

    Args:
      component: Could be ``"client"``, ``"inference"``, ``"verification"``, or ``None``
    """
    return object_name(Entities.Evaluation, id, component)


def evaluation_manifest(spec: dict) -> dict:
    return {
        "apiVersion": _DYFF_API_VERSION,
        "kind": "Evaluation",
        "metadata": {
            "name": evaluation_name(spec["id"]),
            "labels": {
                f"{_DYFF_GROUP}/workflow": "evaluation",
                f"{_DYFF_GROUP}/component": "evaluation",
                f"{_DYFF_GROUP}/account": spec["account"],
                f"{_DYFF_GROUP}/id": spec["id"],
            },
        },
        "spec": to_yaml(spec),
    }


def model_name(id: str, component=None) -> str:
    """Returns the k8s name of a Model-related component.

    Args:
      component: Could be ``"fetch"``, or ``None``
    """
    return object_name(Entities.Model, id, component)


def model_manifest(spec: dict) -> dict:
    return {
        "apiVersion": _DYFF_API_VERSION,
        "kind": "Model",
        "metadata": {
            "name": model_name(spec["id"]),
            "labels": {
                f"{_DYFF_GROUP}/workflow": "model",
                f"{_DYFF_GROUP}/component": "model",
                f"{_DYFF_GROUP}/account": spec["account"],
                f"{_DYFF_GROUP}/id": spec["id"],
            },
        },
        "spec": to_yaml(spec),
    }


def inference_session_name(id: str, component=None) -> str:
    """Returns the k8s name of an InferenceSession-related component."""
    return object_name(Entities.InferenceSession, id, component)


def inference_session_manifest(spec: dict) -> dict:
    return {
        "apiVersion": _DYFF_API_VERSION,
        "kind": "InferenceSession",
        "metadata": {
            "name": inference_session_name(spec["id"]),
            "labels": {
                f"{_DYFF_GROUP}/workflow": "inferencesession",
                f"{_DYFF_GROUP}/component": "inferencesession",
                f"{_DYFF_GROUP}/account": spec["account"],
                f"{_DYFF_GROUP}/id": spec["id"],
            },
        },
        "spec": to_yaml(spec),
    }


def report_name(id: str, component=None) -> str:
    """Returns the k8s name of a report-related component.

    Args:
      component: Could be ``"run"``, or ``None``
    """
    return object_name(Entities.Report, id, component)


def report_manifest(spec: dict) -> dict:
    return {
        "apiVersion": _DYFF_API_VERSION,
        "kind": "Report",
        "metadata": {
            "name": report_name(spec["id"]),
            "labels": {
                f"{_DYFF_GROUP}/workflow": "report",
                f"{_DYFF_GROUP}/component": "report",
                f"{_DYFF_GROUP}/account": spec["account"],
                f"{_DYFF_GROUP}/id": spec["id"],
            },
        },
        "spec": to_yaml(spec),
    }


def create_resource(kind: Entities | str, body, *, namespace: str) -> Any:
    kind = Entities(kind)
    return k8s.client.CustomObjectsApi().create_namespaced_custom_object(
        group=_DYFF_GROUP,
        version=_DYFF_VERSION,
        namespace=namespace,
        plural=Resources.for_kind(kind).value,
        body=body,
    )


def delete_resource(kind: Entities | str, name: str, *, namespace: str):
    kind = Entities(kind)
    return k8s.client.CustomObjectsApi().delete_namespaced_custom_object(
        group=_DYFF_GROUP,
        version=_DYFF_VERSION,
        name=name,
        namespace=namespace,
        plural=Resources.for_kind(kind).value,
        # Do we want any non-default options?
        body=k8s.client.V1DeleteOptions(),
    )
