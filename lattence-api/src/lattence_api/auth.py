import os
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from fastapi import Header, HTTPException
from lattence.governance import ApiKeyStore, Role

_TOKEN_ENV_VAR = "LATTENCE_API_TOKEN"
_RBAC_DB_ENV_VAR = "LATTENCE_RBAC_DB"


@dataclass(frozen=True)
class AuthenticatedCaller:
    caller_id: str


def _rbac_store() -> ApiKeyStore | None:
    configured = os.environ.get(_RBAC_DB_ENV_VAR)
    if not configured:
        return None
    return ApiKeyStore(Path(configured))


def require_access(role: Role) -> Callable[[str | None], AuthenticatedCaller]:
    def dependency(
        authorization: str | None = Header(default=None),
    ) -> AuthenticatedCaller:
        legacy_token = os.environ.get(_TOKEN_ENV_VAR)
        store = _rbac_store()
        if not legacy_token and store is None:
            raise HTTPException(
                status_code=503,
                detail=f"{_TOKEN_ENV_VAR} is not configured on the server",
            )
        if authorization is None or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing bearer token")
        presented = authorization.removeprefix("Bearer ")

        if store is not None:
            identity = store.resolve(presented)
            if identity is not None:
                if role not in identity.roles:
                    raise HTTPException(
                        status_code=403,
                        detail=f"caller {identity.caller_id} lacks role {role.value}",
                    )
                return AuthenticatedCaller(identity.caller_id)

        if legacy_token and secrets.compare_digest(presented, legacy_token):
            return AuthenticatedCaller("team-token")

        raise HTTPException(status_code=401, detail="invalid bearer token")

    return dependency
