# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import pyarrow


def Image():
    return pyarrow.struct(
        [
            pyarrow.field("bytes", pyarrow.binary()),
            pyarrow.field("format", pyarrow.string()),
        ]
    )


def TextSpan(name: str):
    return pyarrow.field(
        name,
        pyarrow.struct(
            [
                pyarrow.field(
                    "start",
                    pyarrow.int64(),
                    metadata={
                        "__doc__": "The tag applies to the slice start:end of the text."
                    },
                ),
                pyarrow.field(
                    "end",
                    pyarrow.int64(),
                    metadata={
                        "__doc__": "The tag applies to the slice start:end of the text."
                    },
                ),
                pyarrow.field(
                    "tag",
                    pyarrow.string(),
                    metadata={"__doc__": "The tag of the span."},
                ),
            ]
        ),
        metadata={"__doc__": "Associates a tag with a text slice."},
    )
