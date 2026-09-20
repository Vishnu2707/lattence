from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from lattence.cli.presentation_workflow import create_security_presentation
from lattence.evidence import SecurityPresentation
from lattence.governance import Role

from ..auth import AuthenticatedCaller, require_access

router = APIRouter()


@router.get("/v1/chain", response_model=SecurityPresentation)
def chain(
    caller: Annotated[AuthenticatedCaller, Depends(require_access(Role.READ_FINDINGS))],
    path: str = ".",
) -> SecurityPresentation:
    del caller
    try:
        return create_security_presentation(Path(path))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
