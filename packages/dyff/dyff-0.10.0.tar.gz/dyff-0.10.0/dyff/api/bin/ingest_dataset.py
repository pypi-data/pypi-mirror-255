# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import absl.app
import absl.flags

from ..data import ingest

# -----------------------------------------------------------------------------

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string(
    "dataset_yaml", None, "YAML file describing how to parse the dataset."
)
absl.flags.mark_flag_as_required("dataset_yaml")

absl.flags.DEFINE_bool(
    "dryrun",
    False,
    "Parse the YAML file and check paths, etc., but don't run anything.",
)

# -----------------------------------------------------------------------------


def main(unused_argv):
    ingest.ingest(FLAGS.dataset_yaml, dryrun=FLAGS.dryrun)


if __name__ == "__main__":
    absl.app.run(main)
