# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import shutil
import urllib
from pathlib import Path

import requests

from ...api.typing import PathLike


def download_file(url: str, *, local_filename: PathLike = None) -> Path:
    """Download a file from a URL.

    Args:
      url: The URL to download from
      local_filename (optional): Local path to save the downloaded file.
        Default: last element of the URL

    Returns:
      The local filename.

    See:
      https://stackoverflow.com/a/39217788
    """
    parsed_url = urllib.parse.urlparse(url)  # Primarily for validity-checking
    if local_filename is None:
        local_filename = Path(parsed_url.path.split("/")[-1])
    else:
        local_filename = Path(local_filename)
    with requests.get(url, stream=True) as r:
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    return local_filename


def fetch_url(
    url: str, *, local_directory: PathLike, local_file: PathLike = None
) -> Path:
    parsed_url = urllib.parse.urlparse(url)  # Primarily for validity-checking
    remote_file = parsed_url.path.split("/")[-1]
    local_file = local_file or remote_file
    local_path = Path(local_directory) / local_file
    download_file(url, local_filename=local_path)
    return local_path
