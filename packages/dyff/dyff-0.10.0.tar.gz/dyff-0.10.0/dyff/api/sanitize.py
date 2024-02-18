# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Union


def sanitize_relative_file_path(path: Union[Path, str]) -> Path:
    """Raises a ``ValueError`` if the provided path is not a relative path that
    is safe to extract files into. An unsafe path is one that either:
      1. is an absolute path
      2. references paths outside of its "root" directory (e.g., "foo/../../bar")

    Returns:
      The fully-resolved relative path
    """
    path = Path(path)
    if path.is_absolute():
        raise ValueError("not a relative path")
    cwd = Path(".")
    # This will raise a ValueError if 'path' refers to a directory that is
    # not a subdirectory of 'cwd' (which, since 'path' is a relative path, means
    # that 'somedir/path' would be outside of 'somedir', which is an exploit).
    return path.resolve().relative_to(cwd.resolve())
