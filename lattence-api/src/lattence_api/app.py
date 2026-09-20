from importlib.metadata import version

from fastapi import FastAPI

from .jobs import JobController
from .routes.attack import router as attack_router
from .routes.chain import router as chain_router
from .routes.jobs import router as jobs_router
from .routes.scan import router as scan_router


def create_app() -> FastAPI:
    app = FastAPI(title="lattence-api", version=version("lattence"))
    app.state.job_controller = JobController()
    app.include_router(scan_router)
    app.include_router(attack_router)
    app.include_router(chain_router)
    app.include_router(jobs_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
