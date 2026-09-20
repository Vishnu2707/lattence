import os
import secrets

from fastapi import Header, HTTPException

_TOKEN_ENV_VAR = "LATTENCE_API_TOKEN"


def require_bearer_token(authorization: str | None = Header(default=None)) -> None:
    configured = os.environ.get(_TOKEN_ENV_VAR)
    if not configured:
        raise HTTPException(
            status_code=503,
            detail=f"{_TOKEN_ENV_VAR} is not configured on the server",
        )
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    presented = authorization.removeprefix("Bearer ")
    if not secrets.compare_digest(presented, configured):
        raise HTTPException(status_code=401, detail="invalid bearer token")
