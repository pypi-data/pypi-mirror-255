# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import absl.app
import absl.flags
from absl import logging

from ...api import timestamp
from ...api.data.sinks import GoogleStorageUploader
from ...api.data.sources import ZenodoRecord

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string("source", None, "The source to obtain the data from.")
absl.flags.mark_flag_as_required("source")

absl.flags.DEFINE_enum("source_kind", None, ["zenodo"], "The kind of source.")
absl.flags.mark_flag_as_required("source_kind")

absl.flags.DEFINE_string(
    "upload_bucket", None, "The name of the GS bucket to store the data in."
)
absl.flags.mark_flag_as_required("upload_bucket")

absl.flags.DEFINE_bool(
    "dryrun",
    False,
    "Set up the fetch operation but don't download data or modify anything.",
)


RETURNCODE_SUCCESS = 0
RETURNCODE_ERROR = 1


def _create_source():
    if FLAGS.source_kind == "zenodo":
        return ZenodoRecord(FLAGS.source)
    else:
        raise ValueError(f"Don't know how to fetch --source_kind={FLAGS.source_kind}")


def main(unused_argv):
    try:
        source = _create_source()
        sink = GoogleStorageUploader(FLAGS.upload_bucket)
        if not FLAGS.dryrun:
            ts_start = timestamp.now()
            logging.info(f"fetch started: {ts_start}")
            source.fetch_into(sink)
            ts_finish = timestamp.now()
            logging.info(f"fetch finished: {ts_finish}")
        return RETURNCODE_SUCCESS
    except:
        logging.exception("fetch may be incomplete")
        return RETURNCODE_ERROR


if __name__ == "__main__":
    absl.app.run(main)
