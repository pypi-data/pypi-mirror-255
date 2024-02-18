#!/usr/bin/env python3
# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import json
import sys

from fastapi.openapi.utils import get_openapi

from dyff.api.api import app

# See: https://github.com/tiangolo/fastapi/issues/1173#issuecomment-605664503
with open(sys.argv[1], "w") as fout:
    json.dump(
        get_openapi(
            title=app.title,
            version=app.version,
            openapi_version="3.0.2",
            description=app.description,
            routes=app.routes,
        ),
        fout,
        indent=2,
    )
