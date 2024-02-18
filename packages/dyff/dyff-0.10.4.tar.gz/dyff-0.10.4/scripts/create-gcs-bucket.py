#!/usr/bin/env python3
# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import secrets

import absl.app
import absl.flags
import google.cloud.exceptions
import google.cloud.storage

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string(
    "category",
    None,
    "Create an s3 bucket named named 'alignmentlabs-<category>-<random ID>'",
)
absl.flags.mark_flag_as_required("category")

absl.flags.DEFINE_integer(
    "conflict_retries",
    5,
    "Number of times to re-try with different random ID if there is a name conflict",
)


RETURNCODE_SUCCESS = 0
RETURNCODE_CONFLICTS = 1


def _next_bucket_name(category):
    hex = secrets.token_hex(8)
    return f"alignmentlabs-{category}-{hex}"


def main(unused_argv):
    client = google.cloud.storage.Client()

    for i in range(FLAGS.conflict_retries):
        bucket_name = _next_bucket_name(FLAGS.category)
        try:
            new_bucket = client.create_bucket(bucket_name, location="us-central1")
        except google.cloud.exceptions.Conflict:
            continue
        else:
            print(f"gs://{bucket_name}")
            return RETURNCODE_SUCCESS
    else:
        print("E: too many name conflicts")
        return RETURNCODE_CONFLICTS


if __name__ == "__main__":
    absl.app.run(main)
