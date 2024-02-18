# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
import absl.app
import absl.flags
from absl import logging

from dyff.audit.scoring import Rubric
from dyff.core import dynamic_import
from dyff.schema.dataset import arrow

# -----------------------------------------------------------------------------

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string(
    "rubric", None, "Qualified Python module name of the Rubric to apply"
)

absl.flags.DEFINE_string("dataset_path", None, "Local path to the Dataset data")

absl.flags.DEFINE_string("evaluation_path", None, "Local path to the Evaluation data")

absl.flags.DEFINE_string(
    "output_path", None, "Local path to where the report output should go"
)

absl.flags.mark_flags_as_required(
    ["rubric", "dataset_path", "evaluation_path", "output_path"]
)

# -----------------------------------------------------------------------------


def main(_unused_argv) -> None:
    logging.set_verbosity(logging.INFO)

    if FLAGS.rubric.startswith("dyff."):
        # Don't accept arbitrary import paths
        rubric = dynamic_import.instantiate(FLAGS.rubric)
    else:
        # Backwards compatibility
        rubric = dynamic_import.instantiate(f"dyff.audit.scoring.{FLAGS.rubric}")
    if not isinstance(rubric, Rubric):
        raise ValueError(f"{FLAGS.rubric} is not a Rubric subclass")

    task_data = arrow.open_dataset(FLAGS.dataset_path)
    outputs_data = arrow.open_dataset(FLAGS.evaluation_path)

    # TODO: We're not doing anything with the DataViews yet

    arrow.write_dataset(
        rubric.apply(task_data, outputs_data),
        output_path=FLAGS.output_path,
        feature_schema=rubric.schema,
    )


if __name__ == "__main__":
    absl.app.run(main)
