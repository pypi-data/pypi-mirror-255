# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import absl.app
import absl.flags
import google.cloud.devtools.cloudbuild_v1 as gcb
import google.cloud.devtools.cloudbuild_v1.types as gcb_types

FLAGS = absl.flags.FLAGS


absl.flags.DEFINE_string("project", None, "The Google Cloud project ID.")
absl.flags.mark_flag_as_required("project")

absl.flags.DEFINE_string(
    "location", None, "The Google Cloud location of the Artifact Registry."
)
absl.flags.mark_flag_as_required("location")

absl.flags.DEFINE_string(
    "source_bucket", None, "The GCS bucket containing the model source."
)
absl.flags.mark_flag_as_required("source_bucket")

absl.flags.DEFINE_string("account", None, "The account identifier of the model owner.")
absl.flags.mark_flag_as_required("account")

absl.flags.DEFINE_string("model", None, "The ID of the model.")
absl.flags.mark_flag_as_required("model")

absl.flags.DEFINE_string("service", None, "The name of the ModelService to build.")
absl.flags.mark_flag_as_required("service")


def main(unused_argv):
    image = f"{FLAGS.location}-docker.pkg.dev/{FLAGS.project}/dyff-models/{FLAGS.account}/{FLAGS.model}"
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
                bucket=FLAGS.source_bucket,
                object_=f"{FLAGS.account}/{FLAGS.model}/{FLAGS.service}.tar.gz",
            )
        ),
        images=[image],
    )

    client = gcb.CloudBuildClient()
    operation = client.create_build(project_id=FLAGS.project, build=build)
    response = operation.result()
    return int(response.status != gcb_types.Build.Status.SUCCESS)


if __name__ == "__main__":
    absl.app.run(main)
