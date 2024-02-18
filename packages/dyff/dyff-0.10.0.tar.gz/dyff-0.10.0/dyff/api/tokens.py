# Copyright UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="import-untyped"
from __future__ import annotations

import secrets
import warnings
from datetime import datetime, timedelta
from typing import Any, Mapping, Optional, Protocol

import jose.jwt
from passlib.hash import bcrypt

from ..schema import ids
from ..schema.platform import AccessGrant, APIKey, Entities
from .backend.base.auth import AuthBackend

ACCOUNT_TOKEN = "account"
EPHEMERAL_TOKEN = "ephemeral"

TOKEN_CHOICES = (
    ACCOUNT_TOKEN,
    EPHEMERAL_TOKEN,
)


class AuthenticationError(RuntimeError):
    pass


class Signer(Protocol):
    """Manages signatures for access tokens."""

    def sign_api_key(self, api_key: APIKey) -> str:
        """Generate a signed token for the given APIKey."""

    def unsign_api_key(self, token: str) -> APIKey:
        """Extract an APIKey from a signed token. Raises an error if the
        signature is invalid.
        """


class NoSigner:
    """Raises AuthenticationError on signature operations."""

    def sign_api_key(self, api_key: APIKey) -> str:
        """Generate a signed token for the given APIKey."""
        raise AuthenticationError("no signer")

    def unsign_api_key(self, token: str) -> APIKey:
        """Extract an APIKey from a signed token. Raises an error if the
        signature is invalid.
        """
        raise AuthenticationError("no signer")


class JWTSigner:
    """Encodes and decodes JSON Web Tokens."""

    algorithm = "HS256"

    def __init__(self, signing_secret: str | bytes | None):
        self._secret = signing_secret

    def _headers(self) -> dict:
        return {"typ": "JWT", "alg": JWTSigner.algorithm}

    def sign_api_key(self, api_key: APIKey) -> str:
        """Generate a signed token for the given APIKey."""
        headers = self._headers()
        payload = {
            "jti": api_key.id,
            "sub": api_key.subject,
            "nbf": api_key.created,
            "exp": api_key.expires,
            "iat": datetime.utcnow(),
            "grants": [g.dict() for g in api_key.grants],
        }
        if api_key.secret is not None:
            payload["secret"] = api_key.secret
        return jose.jwt.encode(
            payload, key=self._secret, algorithm=JWTSigner.algorithm, headers=headers
        )

    def unsign_api_key(self, token: str) -> APIKey:
        """Extract an APIKey from a signed token. Raises an error if the
        signature is invalid.
        """
        return self._unsign_api_key(token)

    def _unsign_api_key(
        self, token: str, *, decode_options: Optional[Mapping[str, Any]] = None
    ) -> APIKey:
        """Extract an APIKey from a signed token. Raises an error if the
        signature is invalid.
        """
        options = {"require": ["jti", "sub", "nbf", "exp", "iat"]}
        if decode_options:
            options.update(decode_options)
        payload = jose.jwt.decode(
            token, key=self._secret, algorithms=JWTSigner.algorithm, options=options
        )
        return APIKey.parse_obj(
            dict(
                id=payload["jti"],
                subject=payload["sub"],
                created=payload["nbf"],
                expires=payload["exp"],
                secret=payload.get("secret"),
                grants=payload["grants"],
            )
        )


def get_signer(signing_secret: str | None) -> Signer:
    if signing_secret is not None:
        return JWTSigner(signing_secret)
    else:
        return NoSigner()


def generate_api_key(
    *,
    subject_type: Entities,
    subject_id: str,
    grants: Optional[list[AccessGrant]] = None,
    expires: Optional[datetime] = None,
    generate_secret: bool = False,
) -> APIKey:
    """Generates a new API key for a user. User keys have a secret that uniquely
    identifies the user account.
    """
    if grants is None:
        warnings.warn("Creating an API key with no access grants")
        grants = []
    instance_secret = secrets.token_urlsafe(16) if generate_secret else None
    now = datetime.utcnow()
    if expires is None:
        expires = now + timedelta(days=365)
    return APIKey(
        id=ids.generate_entity_id(),
        subject=f"{subject_type}/{subject_id}",
        created=now,
        expires=expires,
        secret=instance_secret,
        grants=grants,
    )


def hashed_api_key(api_key: APIKey) -> APIKey:
    """Returns a new APIKey where the ``.secret`` field is cryptographically
    hashed.
    """
    return api_key.copy(update={"secret": bcrypt.hash(api_key.secret)})


def verify_api_key_hash(api_key: APIKey, hashed_key: APIKey) -> bool:
    """Returns True if ``api_key.secret`` matches ``hashed_key.secret``."""
    return bcrypt.verify(api_key.secret, hashed_key.secret)


def verify_api_token(
    token: str, signer: Signer, *, auth_backend: Optional[AuthBackend] = None
) -> APIKey:
    """Verifies the token and returns its "payload" as a JSON dict. Raises an
    exception if the signature is invalid or if the secret doesn't match the
    hashed secret in the datastore.
    """
    try:
        unsigned_key = signer.unsign_api_key(token)
    except Exception as ex:
        raise AuthenticationError("bad signature") from ex

    # Only user keys have a secret
    if unsigned_key.secret is not None:
        if auth_backend is None:
            raise AssertionError("no auth_backend provided")
        kind, account, *rest = unsigned_key.subject.split("/")
        if kind != Entities.Account or len(rest) != 0:
            raise AuthenticationError("expected subject = 'Account/id'")
        stored_key = auth_backend.get_api_key(account, unsigned_key.id)
        if (stored_key is None) or (not verify_api_key_hash(unsigned_key, stored_key)):
            raise AuthenticationError("unverified")

    return unsigned_key
