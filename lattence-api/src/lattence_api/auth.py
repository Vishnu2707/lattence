import os
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from fastapi import Header, HTTPException
from lattence.governance import ApiKeyStore, Role

from .sso import active_sso_provider

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


def _require_role(role: Role, identity_caller_id: str, roles: frozenset[Role]) -> None:
    if role not in roles:
        raise HTTPException(
            status_code=403,
            detail=f"caller {identity_caller_id} lacks role {role.value}",
        )


def require_access(role: Role) -> Callable[[str | None], AuthenticatedCaller]:
    def dependency(
        authorization: str | None = Header(default=None),
    ) -> AuthenticatedCaller:
        legacy_token = os.environ.get(_TOKEN_ENV_VAR)
        store = _rbac_store()
        provider = active_sso_provider()
        if not legacy_token and store is None and provider is None:
            raise HTTPException(
                status_code=503,
                detail=f"{_TOKEN_ENV_VAR} is not configured on the server",
            )
        if authorization is None or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="missing bearer token")
        presented = authorization.removeprefix("Bearer ")

        if provider is not None:
            identity = provider.resolve(presented)
            if identity is not None:
                _require_role(role, identity.caller_id, identity.roles)
                return AuthenticatedCaller(identity.caller_id)

        if store is not None:
            identity = store.resolve(presented)
            if identity is not None:
                _require_role(role, identity.caller_id, identity.roles)
                return AuthenticatedCaller(identity.caller_id)

        if legacy_token and secrets.compare_digest(presented, legacy_token):
            return AuthenticatedCaller("team-token")

        raise HTTPException(status_code=401, detail="invalid bearer token")

    return dependency
