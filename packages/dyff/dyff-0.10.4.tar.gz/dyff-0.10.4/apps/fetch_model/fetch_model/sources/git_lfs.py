# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import subprocess

from dyff.schema.platform import ModelSourceGitLFS


def fetch(local_path: str, spec: ModelSourceGitLFS):
    print(f"cloning: {spec.url}")
    subprocess.run(["git", "clone", spec.url, local_path], check=True)
    # TODO: Only download the "preferred" format of the model weights
    # (HF repos can have multiple copies for different frameworks)
    print(f"lfs fetch: {spec.url}")
    subprocess.run(["git", "lfs", "fetch"], cwd=local_path, check=True)
