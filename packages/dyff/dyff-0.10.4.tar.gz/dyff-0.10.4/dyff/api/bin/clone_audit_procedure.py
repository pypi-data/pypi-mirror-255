# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import absl.app
import absl.flags
import gitlab
from absl import logging

from ...core.config import config

# ----------------------------------------------------------------------------

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_string(
    "remote_path",
    None,
    "Path to the root of the audit procedure code in the remote repository.",
)
absl.flags.DEFINE_string("local_path", None, "Local path to clone into.")
absl.flags.mark_flags_as_required(["remote_path", "local_path"])

# ----------------------------------------------------------------------------


def clone_gitlab_resources(remote_path: Path, local_path: Path, *, ref: str = "HEAD"):
    client = gitlab.Gitlab(private_token=config.gitlab.audit_reader_access_token)
    project = client.projects.get(config.storage.audit_leaderboards_gitlab_project)
    for d in project.repository_tree(path=str(remote_path), recursive=True):
        if d["type"] != "blob":
            continue
        remote_file = d["path"]
        # Strip directory prefix from remote path
        relative_file_path = Path(remote_file).relative_to(remote_path)
        local_file = local_path / relative_file_path
        local_file.parent.mkdir(exist_ok=True, parents=True)
        with open(local_file, "wb") as fout:
            project.files.raw(remote_file, ref=ref, streamed=True, action=fout.write)


def main(_unused_argv):
    logging.set_verbosity(logging.INFO)
    remote_path = Path(FLAGS.remote_path)
    local_path = Path(FLAGS.local_path)
    clone_gitlab_resources(remote_path, local_path)


if __name__ == "__main__":
    absl.app.run(main)
