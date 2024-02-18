# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
from __future__ import annotations

from typing import NamedTuple, Sequence

import absl.app
import absl.flags
from absl import logging

from dyff.api import storage

FLAGS = absl.flags.FLAGS

absl.flags.DEFINE_multi_string(
    "transfer",
    None,
    "A string like 'gs://source/foo>/local/bar'."
    " Note the '>' character separating source and destination."
    " The *entire directory* 'foo' will end up at '/local/bar/foo'."
    " If source is a storage path and destination is a filesystem path,"
    " download from storage."
    " If source is a local path and destination is a storage path,"
    " upload to storage.",
)
absl.flags.mark_flags_as_required(["transfer"])


class ResourceLocation(NamedTuple):
    path: str
    protocol: str

    def uri(self) -> str:
        if self.protocol == "filesystem":
            return self.path
        else:
            return f"{self.protocol}://{self.path}"

    @staticmethod
    def from_path(path: str) -> ResourceLocation:
        parts = path.split("://")
        if len(parts) == 1:
            return ResourceLocation(path=parts[0], protocol="filesystem")
        elif len(parts) == 2:
            return ResourceLocation(path=parts[1], protocol=parts[0])
        else:
            raise ValueError(
                "expected filesystem path (/some/path) or storage path (gs://bucket/path)"
                f"; got '{path}'"
            )


class Transfer(NamedTuple):
    source: ResourceLocation
    destination: ResourceLocation


def main(_argv: Sequence[str]):
    supported_protocols = ["filesystem", "gs"]
    # Validate everything first
    transfers: list[Transfer] = []
    for command in FLAGS.transfer:
        source_path, destination_path = str(command).split(">")
        transfer = Transfer(
            source=ResourceLocation.from_path(source_path.strip()),
            destination=ResourceLocation.from_path(destination_path.strip()),
        )
        if not (
            (transfer.source.protocol == "filesystem")
            ^ (transfer.destination.protocol == "filesystem")
        ):
            raise NotImplementedError(
                "only storage>filesystem and filesystem>storage are implemented"
            )
        if transfer.source.protocol not in supported_protocols:
            raise NotImplementedError(
                f"unsupported protocol {transfer.source.protocol}"
            )
        if transfer.destination.protocol not in supported_protocols:
            raise NotImplementedError(
                f"unsupported protocol {transfer.destination.protocol}"
            )
        transfers.append(transfer)

    for transfer in transfers:
        if transfer.source.protocol != "filesystem":
            logging.info(
                f"download: {transfer.source.uri()} > {transfer.destination.uri()}"
            )
            storage.download_recursive(
                transfer.source.uri(), transfer.destination.uri()
            )
        elif transfer.destination.protocol != "filesystem":
            logging.info(
                f"upload: {transfer.source.uri()} > {transfer.destination.uri()}"
            )
            storage.upload_recursive(transfer.source.uri(), transfer.destination.uri())
        else:
            raise AssertionError()


if __name__ == "__main__":
    absl.app.run(main)
