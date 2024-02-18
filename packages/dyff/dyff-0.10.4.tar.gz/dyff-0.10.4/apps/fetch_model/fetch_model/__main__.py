# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
import contextlib
import tarfile
import tempfile

import absl.app
import absl.flags
import ruamel.yaml
import smart_open
from absl import logging

from dyff.api import storage, timestamp
from dyff.schema.platform import ModelSource

from .fetch import fetch

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string(
    "model_yaml", None, "Path to a YAML file containing the Model manifest."
)
absl.flags.mark_flag_as_required("model_yaml")

absl.flags.DEFINE_string(
    "local_dir",
    None,
    "Directory to fetch the model into. This can be an ephemeral directory if"
    " you just want the model to end up in s3, or a presistent volume if you"
    " want the model in a PVC. If not specified, a temp directory will be created.",
)

absl.flags.DEFINE_bool(
    "debug_log_disk_usage",
    False,
    "Run a background thread that prints disk usage information."
    " Useful for figuring out where BentoML / OpenLLM are storing things.",
)

absl.flags.DEFINE_bool(
    "debug_no_storage_upload",
    False,
    "Disable upload to object storage for faster debugging",
)


RETURNCODE_SUCCESS = 0
RETURNCODE_ERROR = 1


def _local_dir_context(local_dir: str):
    if local_dir is not None:
        return contextlib.nullcontext(local_dir)
    else:
        return tempfile.TemporaryDirectory()


def main(unused_argv):
    if FLAGS.debug_log_disk_usage:
        import subprocess
        import threading
        import time

        def _watch_du():
            while True:
                subprocess.run(
                    "for d in /*; do du -sh $d; done", shell=True, check=True
                )
                time.sleep(1.0)

        monitor_daemon = threading.Thread(
            target=_watch_du, daemon=True, name="watch_du"
        )
        monitor_daemon.start()

    yaml = ruamel.yaml.YAML()
    with open(FLAGS.model_yaml, "r") as fin:
        model = yaml.load(fin)

    try:
        with _local_dir_context(FLAGS.local_dir) as local_dir:
            model_id = model["spec"]["id"]
            source = ModelSource.parse_obj(model["spec"]["source"])

            ts_start = timestamp.now()
            logging.info(f"fetch started: {ts_start}")

            fetch(local_dir, source)

            ts_finish = timestamp.now()
            logging.info(f"fetch finished: {ts_finish}")

            if not FLAGS.debug_no_storage_upload:
                # Note: We're gzipping via tarfile, so we disable compression for
                # smart_open (which would otherwise infer it from .gz). It seems to work
                # without disabling compression, but we'll do it anyway just to be safe.
                with smart_open.open(
                    storage.paths.model_source_archive(model_id),
                    "wb",
                    compression="disable",
                ) as fout:
                    with tarfile.open(fileobj=fout, mode="w|gz") as tar:
                        # arcname="." because we want paths in the tar archive to be relative
                        # to the bento root directory
                        tar.add(local_dir, arcname=".", recursive=True)
        return RETURNCODE_SUCCESS
    except:
        logging.exception("fetch may be incomplete")
        return RETURNCODE_ERROR


if __name__ == "__main__":
    absl.app.run(main)
