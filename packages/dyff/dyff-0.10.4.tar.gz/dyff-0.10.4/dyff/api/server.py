# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

"""Web server for the dyff platform.
"""

import logging
from contextlib import asynccontextmanager

import fastapi

from ..core.config import config
from . import api


class EndpointFilter(logging.Filter):
    def __init__(self, path: str, *args, verb: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._path = path
        self._verb = verb

    def filter(self, record):
        (
            remote_address,
            verb,
            query_string,
            html_version,
            status_code,
            *rest,
        ) = record.args
        return not all(
            [
                self._verb is None or verb == self._verb,
                query_string.startswith(self._path),
            ]
        )


try:
    import uvicorn.config

    # Filter out log messages about the '/health' endpoint, because they happen
    # a lot and they're not interesting.
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addFilter(EndpointFilter(path="/health"))
    uvicorn.config.LOGGING_CONFIG["loggers"]["api-server"] = {
        "handlers": ["default"],
        "level": logging.INFO,
    }
except Exception:
    pass


@asynccontextmanager
async def _lifespan(app: fastapi.FastAPI):
    # FIXME: Try as I might, I can't get logging to print anything unless I go
    # through the 'uvicorn' logger. Since all I really want to do is see the
    # configuration, I'm just going to use a print() for now.
    # log = logging.getLogger("api-server")
    # log.info(f"aStarting API server with configuration:\n{config.json(indent=2)}")
    # log = logging.getLogger("uvicorn")
    # log.info(f"bStarting API server with configuration:\n{config.json(indent=2)}")
    print(
        f"Starting API server with configuration:\n{config.json(indent=2)}", flush=True
    )
    yield


app = fastapi.FastAPI(
    title="dyff",
    lifespan=_lifespan,
)
app.mount("/dyff/v0", api.app)


@app.get(f"/health")
async def health() -> int:
    """Required health check for GKE Ingress. Should be specified in the
    k8s Deployment as a readinessProbe.
    """
    return fastapi.status.HTTP_200_OK
