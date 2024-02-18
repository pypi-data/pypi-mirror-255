# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

import pydantic

VERSION: str = "0.1"


class Versioned(pydantic.BaseModel):
    schemaVersion: Literal["0.1"] = pydantic.Field(
        default=VERSION, description="The schema version."
    )


__all__ = [
    "VERSION",
    "Versioned",
]
