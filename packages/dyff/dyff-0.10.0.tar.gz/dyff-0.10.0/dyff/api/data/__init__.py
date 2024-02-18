# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import base64
import hashlib
from typing import Dict, List

import pyarrow

from ..typing import PathLike


def parse_dataset_filters(filters: List[Dict]):
    filter_expression = None
    for f in filters:
        field = pyarrow.compute.field(f["field"])
        value = f["value"]
        relation = f["relation"]
        if relation == "==":
            expr = field == value
        elif relation == "!=":
            expr = field != value
        else:
            raise NotImplementedError()

        if filter_expression is None:
            filter_expression = expr
        else:
            filter_expression &= expr
    return filter_expression


def content_hash(content: bytes) -> str:
    h = hashlib.sha256()
    h.update(content)
    return h.hexdigest()


def google_storage_md5(
    *, data: bytes = None, file: PathLike = None, md5_hex: str = None
) -> str:
    if sum(int(x is not None) for x in [data, file, md5_hex]) != 1:
        raise ValueError("must specify exactly 1 argument")

    h = hashlib.md5()
    if data:
        h.update(data)
        digest = h.digest()
    elif file:
        with open(file, "rb") as fin:
            h.update(fin.read())
        digest = h.digest()
    else:
        digest = bytes.fromhex(md5_hex)
    return base64.b64encode(digest).decode()


def file_checksum(file: PathLike, *, algorithm="md5", format="hex") -> str:
    if algorithm == "md5":
        h = hashlib.md5()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    with open(file, "rb") as fin:
        h.update(fin.read())

    if format == "hex":
        return h.hexdigest()
    elif format == "base64":
        return base64.b64encode(h.digest()).decode()
    else:
        raise ValueError(f"Unsupported format: {format}")


def verify_file_checksum(file: PathLike, checksum: bytes) -> bool:
    algorithm, digest = checksum.split(":")
    return digest == file_checksum(file, algorithm=algorithm)
