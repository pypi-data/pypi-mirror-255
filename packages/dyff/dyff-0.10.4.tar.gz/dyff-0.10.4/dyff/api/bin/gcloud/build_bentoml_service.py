# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import contextlib
import copy
import json
import tarfile
import tempfile
from typing import Optional

import absl.app
import absl.flags
import bentoml
import google.cloud.devtools.cloudbuild_v1 as gcb
import google.cloud.devtools.cloudbuild_v1.types as gcb_types
import ruamel.yaml
import smart_open
from absl import logging

from dyff.api import storage
from dyff.core.config import config
from dyff.schema.platform import InferenceServiceSources

from ...models import api as models_api
from .. import storage
from ..backend.gcp.query import DatastoreQueryBackend

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string(
    "inference_service_yaml",
    None,
    "Path to a YAML file containing the InferenceService manifest.",
)
absl.flags.mark_flag_as_required("inference_service_yaml")

absl.flags.DEFINE_string(
    "scratch_dir",
    None,
    "Directory to use for intermediate files. If not specified, a temp directory"
    " will be created.",
)


RETURNCODE_SUCCESS = 0
RETURNCODE_ERROR = 1


def _scratch_dir_context(scratch_dir: str):
    if scratch_dir is not None:
        return contextlib.nullcontext(scratch_dir)
    else:
        return tempfile.TemporaryDirectory("alignmentlabs")


class InferenceServiceGCloudBuildError(RuntimeError):
    def __init__(self, status):
        super().__init__(f"gcloud build error: {status}")
        self.status = status


def gcloud_build_inference_service_image(
    *,
    location: str,
    project: str,
    inference_service: str,
    inference_service_bucket: Optional[str] = None,
):
    if inference_service_bucket is None:
        inference_service_bucket = config.resources.inferenceservices.storage.url

    image = f"{location}-docker.pkg.dev/{project}/dyff-models/{inference_service}"
    build = gcb.Build(
        steps=[
            gcb_types.BuildStep(
                name="gcr.io/cloud-builders/docker",
                args=[
                    "buildx",
                    "build",
                    f"--tag={image}",
                    "--file=env/docker/Dockerfile",
                    ".",
                ],
            )
        ],
        source=gcb_types.Source(
            storage_source=gcb_types.StorageSource(
                # API doesn't accept bucket paths that start with 'gs://'
                bucket=storage.bucket_name_from_path(inference_service_bucket),
                object_=f"{inference_service}/{storage.inference_service_source_archive_name()}",
            )
        ),
        images=[image],
    )

    client = gcb.CloudBuildClient()
    operation = client.create_build(project_id=project, build=build, timeout=1800)
    response = operation.result(timeout=1800)
    if response.status != gcb_types.Build.Status.SUCCESS:
        raise InferenceServiceGCloudBuildError(response.status)


def main(unused_argv):
    # TODO: Make backend configurable
    queries = DatastoreQueryBackend()

    yaml = ruamel.yaml.YAML()
    with open(FLAGS.inference_service_yaml, "r") as fin:
        inference_service = yaml.load(fin)

    try:
        source_kind = inference_service["spec"]["sourceKind"]
        if source_kind != InferenceServiceSources.build:
            raise ValueError(
                f"sourceKind={source_kind}: expected {InferenceServiceSources.build}"
            )
        service_id = inference_service["spec"]["id"]
        model_id = inference_service["spec"]["source"]
        task_id = inference_service["spec"]["task"]
        task = queries.get_task(task_id)
        output_path = f"{config.resources.inferenceservices.storage.url}/{service_id}"

        with _scratch_dir_context(FLAGS.scratch_dir) as scratch:
            # Pull raw model from bucket to local filesystem
            fetch_dir = f"{scratch}/fetch"
            model_source_path = storage.paths.model_source_archive(model_id)
            with smart_open.open(model_source_path, "rb", compression="disable") as fin:
                with tarfile.open(fileobj=fin, mode="r|gz") as tar:
                    tar.extractall(fetch_dir)
            model_interface = models_api.get_model_interface(
                inference_service["spec"]["interface"], task
            )

            metadata = copy.deepcopy(inference_service)
            metadata["bentoml"] = {"version": bentoml.__version__}

            bento = models_api.create_bento(
                model_interface=model_interface,
                model_tag=model_id,
                service_name=service_id,
                input_path=fetch_dir,
                output_path=output_path,
                scratch_dir=scratch,
            )

            with smart_open.open(f"{output_path}/metadata.json", "w") as fout:
                json.dump(metadata, fout)

            # FIXME: Don't hard-code cluster info
            gcloud_build_inference_service_image(
                location="us-central1",
                project="dyff-354017",
                inference_service=service_id,
            )

        return RETURNCODE_SUCCESS
    except:
        logging.exception("build may be incomplete")
        return RETURNCODE_ERROR


if __name__ == "__main__":
    absl.app.run(main)
