from importlib.metadata import version

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="lattence-api", version=version("lattence"))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
