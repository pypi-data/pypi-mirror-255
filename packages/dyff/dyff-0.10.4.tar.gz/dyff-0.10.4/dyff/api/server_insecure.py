# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

"""Testing version of the Web server for the dyff platform.
"""

import os
import warnings

import fastapi

from dyff.schema.platform import APIKey

from ..web import routes as web_routes
from . import api, tokens


def _not_kubernetes() -> None:
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        raise fastapi.HTTPException(
            fastapi.status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Test configuration is not to be deployed!",
        )


class NonVerifyingJWTSigner(tokens.JWTSigner):
    def __init__(self):
        super().__init__(None)

    def unsign_api_key(self, token: str) -> APIKey:
        warnings.warn("Not verifying JWT signature")
        return super()._unsign_api_key(
            token, decode_options={"verify_signature": False}
        )


api.get_api_key_signer = NonVerifyingJWTSigner


app = fastapi.FastAPI(
    title="dyff",
)
# api.app.dependency_overrides[api.verify_api_token] = _not_kubernetes
app.mount("/dyff/v0", api.app)
app.mount("/web", web_routes.app)
# apps.site.app.dependency_overrides[apps.site.verify_api_token] = _not_kubernetes


@app.get(f"/health")
async def health() -> int:
    """Required health check for GKE Ingress. Should be specified in the
    k8s Deployment as a readinessProbe.
    """
    return fastapi.status.HTTP_200_OK
