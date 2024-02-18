# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import tarfile
from pathlib import Path
from typing import Iterable, Iterator, NamedTuple, Optional

import gcsfs

from ...api.typing import PathLike


class ArchiveEntry(NamedTuple):
    """A single entry in an archive, represented by its path and its raw bytes."""

    path: str
    bytes: bytes


Archive = Iterable[ArchiveEntry]


# TODO: Untested
class DirectoryTree:
    def __init__(self, path: PathLike):
        self._path = path

    def __iter__(self) -> Iterator[ArchiveEntry]:
        path = Path(self._path)
        for member in path.rglob("*"):
            if member.is_file():
                with open(member, "rb") as fin:
                    entry = ArchiveEntry(
                        path=member.relative_to(path), bytes=fin.read()
                    )
                yield entry


class TarArchive:
    def __init__(self, path: PathLike, *, prefix: Optional[PathLike] = None):
        """
        Args:
          path: Path to the archive. Could be a local path or a gs:// path.
          prefix: Path prefix to add to .path fields of the archive entries. This
            can be used to expose things like the archive name as path elements
            that will get processed by the feature extractor.
        """
        self._path = str(path)  # gs:// paths aren't valid as Path objects
        self._prefix = Path(prefix)

    def _iter(self, fin):
        # Open in (streaming mode, transparent compression)
        with tarfile.open(fileobj=fin, mode="r|*") as tar:
            for member in tar:
                if member.isfile():
                    name = Path(member.name)
                    if self._prefix is not None:
                        name = self._prefix / name
                    yield ArchiveEntry(
                        path=str(name), bytes=tar.extractfile(member).read()
                    )

    def __iter__(self) -> Iterator[ArchiveEntry]:
        if self._path.startswith("gs://"):
            # Google Cloud Storage path
            gs = gcsfs.GCSFileSystem()
            with gs.open(self._path, "rb") as fin:
                yield from self._iter(fin)
        else:
            with open(self._path, "rb") as fin:
                yield from self._iter(fin)
