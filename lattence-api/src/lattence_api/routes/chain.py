from pathlib import Path

from fastapi import APIRouter, HTTPException
from lattence.cli.presentation_workflow import create_security_presentation
from lattence.evidence import SecurityPresentation

router = APIRouter()


@router.get("/v1/chain", response_model=SecurityPresentation)
def chain(path: str = ".") -> SecurityPresentation:
    try:
        return create_security_presentation(Path(path))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
