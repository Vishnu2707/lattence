from importlib.metadata import version

from fastapi import FastAPI

from .routes.scan import router as scan_router


def create_app() -> FastAPI:
    app = FastAPI(title="lattence-api", version=version("lattence"))
    app.include_router(scan_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
