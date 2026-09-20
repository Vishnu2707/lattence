from typing import Annotated

import typer

HostOption = Annotated[str, typer.Option("--host")]
PortOption = Annotated[int, typer.Option("--port")]


def serve(host: HostOption = "127.0.0.1", port: PortOption = 8000) -> None:
    try:
        import uvicorn
        from lattence_api import create_app
    except ImportError as error:
        raise typer.BadParameter(
            "the API server requires the api extra: install with "
            "`pip install lattence[api]`"
        ) from error
    uvicorn.run(create_app(), host=host, port=port)
