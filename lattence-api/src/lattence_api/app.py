from importlib.metadata import version

from fastapi import Depends, FastAPI

from .auth import require_bearer_token
from .routes.attack import router as attack_router
from .routes.chain import router as chain_router
from .routes.scan import router as scan_router


def create_app() -> FastAPI:
    app = FastAPI(title="lattence-api", version=version("lattence"))
    authenticated = [Depends(require_bearer_token)]
    app.include_router(scan_router, dependencies=authenticated)
    app.include_router(attack_router, dependencies=authenticated)
    app.include_router(chain_router, dependencies=authenticated)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
