# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

"""This is where we translate from the Dyff API schema to the Dyff k8s operator
schema.

A primary design goal for the k8s operator is that it should be useful
without the rest of the Dyff system. Meaning, for example,
* The operator can't look up other resources by reference, since it doesn't
  have a database.
* We want the k8s API to be more stable than the Dyff API, so it has to allow
  for more customization.

The two schemas share a lot of common structure, but as things have grown
more complex they have needed to diverge to prevent excessive coupling between
the k8s operator and the rest of the system.
"""

from __future__ import annotations

import json
from typing import Any, Optional
from urllib.parse import urlparse

from dyff.core.config import config
from dyff.orchestrator.k8s import resources
from dyff.schema.platform import (
    Dataset,
    DyffEntityType,
    Evaluation,
    InferenceService,
    InferenceServiceRunnerKind,
    InferenceSession,
    InferenceSessionSpec,
    Model,
    ModelArtifactKind,
    ModelStorageMedium,
    Report,
    SchemaAdapter,
)


def manifest(entity: DyffEntityType) -> Optional[dict]:
    if isinstance(entity, Dataset):
        # Currently not supporting a "fetch_data" operation
        return None
    elif isinstance(entity, Evaluation):
        return evaluation_manifest(entity)
    elif isinstance(entity, InferenceService):
        return inference_service_manifest(entity)
    elif isinstance(entity, InferenceSession):
        return inference_session_manifest(entity)
    elif isinstance(entity, Model):
        return model_manifest(entity)
    elif isinstance(entity, Report):
        return report_manifest(entity)
    else:
        raise TypeError(f"entity kind: {entity.kind}")


def model_manifest(model: Model) -> Optional[dict]:
    """Translate a Dyff API ``Model`` to a k8s ``Model``."""
    spec: dict[str, Any] = {
        "id": model.id,
        "account": model.account,
        # Note: We're assuming this sub-schema matches k8s exactly
        "source": model.source.dict(),
    }

    if model.storage.medium == ModelStorageMedium.PersistentVolume:
        spec["storage"] = {
            "kind": "PersistentVolume",
            "persistentVolume": {"storageClassName": "dyff-model"},
        }
    elif model.storage.medium == ModelStorageMedium.ObjectStorage:
        url = urlparse(config.resources.models.storage.url)
        protocol = url.scheme
        bucketName = url.hostname
        spec["storage"] = {
            "kind": "ObjectStore",
            "objectStore": {
                "protocol": protocol,
                "bucketName": bucketName,
            },
        }
    else:
        raise NotImplementedError(f"model.storage.medium: {model.storage.medium}")

    spec["storage"]["quantity"] = model.resources.storage

    return resources.model_manifest(spec)


def inference_service_manifest(inference_service: InferenceService) -> Optional[dict]:
    """Translate a Dyff API ``InferenceService`` to a k8s ``InferenceService``."""
    if inference_service.builder is None:
        # Nothing to do
        return None

    if inference_service.builder.kind == "bentoml-transformers-pipeline":
        # TODO: This is the original build flow for huggingface Pipeline models
        raise NotImplementedError()

    return None


def _inference_session_template_spec(
    session: InferenceSessionSpec,
) -> dict:
    spec: dict[str, Any] = {
        "replicas": session.replicas,
        "useSpotPods": session.useSpotPods,
    }
    # TODO: Define this as a constant somewhere
    model_mount_path = "/dyff/mnt/model"

    service = session.inferenceService
    if service.runner is None:
        raise ValueError(f"InferenceService {service.id} has no .runner")
    if service.model is not None and service.model.storage.medium not in [
        None,
        ModelStorageMedium.PersistentVolume,
    ]:
        raise NotImplementedError(
            f"service.model.storage.medium: {service.model.storage.medium}"
        )

    if service.runner.kind == InferenceServiceRunnerKind.STANDALONE:
        spec["image"] = config.orchestrator.images.standalone.format(service=service)
    elif service.runner.kind == InferenceServiceRunnerKind.MOCK:
        spec["image"] = config.orchestrator.images.mock
    elif service.runner.kind == InferenceServiceRunnerKind.BENTOML_SERVICE_OPENLLM:
        # TODO: Probably just remove this Kind
        raise NotImplementedError()
    elif service.runner.kind in [
        InferenceServiceRunnerKind.HUGGINGFACE,
        InferenceServiceRunnerKind.VLLM,
    ]:
        # Runners for HuggingFace models
        if service.model is None:
            raise ValueError(f"runner {service.runner.kind}: service.model is required")
        if service.model.artifact.kind != ModelArtifactKind.HuggingFaceCache:
            raise ValueError(
                f"runner {service.runner.kind}:"
                f" service.model.artifact.kind must be {ModelArtifactKind.HuggingFaceCache}"
            )
        hf_cache_artifact = service.model.artifact.huggingFaceCache
        assert hf_cache_artifact is not None

        if service.runner.kind == InferenceServiceRunnerKind.HUGGINGFACE:
            spec["image"] = config.orchestrator.images.huggingface
            spec["args"] = [
                "--model_name",
                hf_cache_artifact.repoID,
                "--model_revision",
                hf_cache_artifact.revision,
            ]
        elif service.runner.kind == InferenceServiceRunnerKind.VLLM:
            spec["image"] = config.orchestrator.images.vllm
            spec["args"] = [
                "--model",
                f"{model_mount_path}/{hf_cache_artifact.snapshot_path()}",
                "--download-dir",
                model_mount_path,
            ]
        else:
            raise AssertionError(f"Unexpected runner: {service.runner.kind}")

        if service.runner.args:
            spec["args"].extend(service.runner.args)
        # Some of these are allegedly redundant, but I don't trust HF not
        # to break things
        spec["env"] = [
            {"name": "HF_DATASETS_OFFLINE", "value": "1"},
            {"name": "HF_HOME", "value": model_mount_path},
            {"name": "HUGGINGFACE_HUB_CACHE", "value": model_mount_path},
            {"name": "TRANSFORMERS_CACHE", "value": model_mount_path},
            {"name": "TRANSFORMERS_OFFLINE", "value": "1"},
            {"name": "HF_MODULES_CACHE", "value": "/tmp/hf_modules"},
        ]
        spec["dependencies"] = [
            {
                "kind": "ReadOnlyVolume",
                "readOnlyVolume": {
                    "name": "model",
                    "claimName": f"model-{service.model.id}-rox",
                    "mountPath": model_mount_path,
                },
            }
        ]
    else:
        raise NotImplementedError(f"service.runner.kind {service.runner.kind}")

    session_resources = {
        # defaults
        "requests": {
            "memory": "4Gi",
        }
    }
    if service.runner.resources is not None:
        session_resources["requests"].update(
            {k: v for k, v in service.runner.resources if k in ["cpu", "memory"]}
        )
    spec["resources"] = session_resources

    if session.accelerator is not None:
        spec["accelerator"] = session.accelerator.dict()
    elif service.runner.accelerator is not None:
        spec["accelerator"] = service.runner.accelerator.dict()

    return spec


def inference_session_manifest(inference_session: InferenceSession) -> Optional[dict]:
    """Translate a Dyff API ``InferenceSession`` to a k8s ``InferenceSession``."""
    spec: dict[str, Any] = {
        "id": inference_session.id,
        "account": inference_session.account,
    }
    template_spec = _inference_session_template_spec(inference_session)
    spec.update(template_spec)
    return resources.inference_session_manifest(spec)


def evaluation_manifest(evaluation: Evaluation) -> Optional[dict]:
    """Translate a Dyff API ``Evaluation`` to a k8s ``Evaluation``."""
    # Adapters take arbitrary json configuration. k8s can't handle this, so
    # we encode it as a string.
    interface_spec = evaluation.inferenceSession.inferenceService.interface.dict()
    if (inputPipeline := interface_spec.get("inputPipeline")) is not None:
        for adapter in inputPipeline:
            adapter["configuration"] = json.dumps(adapter["configuration"])
    if (outputPipeline := interface_spec.get("outputPipeline")) is not None:
        for adapter in outputPipeline:
            adapter["configuration"] = json.dumps(adapter["configuration"])
    spec: dict[str, Any] = {
        "id": evaluation.id,
        "account": evaluation.account,
        "dataset": evaluation.dataset,
        "inferenceSession": _inference_session_template_spec(
            evaluation.inferenceSession
        ),
        "interface": interface_spec,
        "replications": evaluation.replications,
        "workersPerReplica": evaluation.workersPerReplica,
    }
    return resources.evaluation_manifest(spec)


def report_manifest(report: Report) -> Optional[dict]:
    """Translate a Dyff API ``Report`` to a k8s ``Report``."""

    def pipeline_configuration(adapters: list[SchemaAdapter]):
        pipeline_json = []
        for adapter in adapters:
            pipeline_json.append(
                {
                    "kind": adapter.kind,
                    "configuration": json.dumps(adapter.configuration),
                }
            )
        return pipeline_json

    spec = {
        "id": report.id,
        "account": report.account,
        "report": report.rubric,
        "dataset": report.dataset,
        "evaluation": report.evaluation,
    }
    if report.datasetView is not None:
        if report.datasetView.adapterPipeline:
            spec["datasetAdapter"] = pipeline_configuration(
                report.datasetView.adapterPipeline
            )
    if report.evaluationView is not None:
        if report.evaluationView.adapterPipeline:
            spec["evaluationAdapter"] = pipeline_configuration(
                report.evaluationView.adapterPipeline
            )
    return resources.report_manifest(spec)
