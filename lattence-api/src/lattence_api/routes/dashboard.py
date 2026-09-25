from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from lattence.cli.presentation_workflow import create_security_presentation
from lattence.cli.workflow import create_report
from lattence.evidence import render_html_report
from lattence.governance import Role

from ..auth import AuthenticatedCaller, require_access

router = APIRouter()


@router.get("/v1/dashboard", response_class=HTMLResponse)
def dashboard(
    caller: Annotated[AuthenticatedCaller, Depends(require_access(Role.READ_FINDINGS))],
    path: str = ".",
) -> HTMLResponse:
    del caller
    resolved = Path(path)
    try:
        report = create_report(resolved)
        presentation = create_security_presentation(resolved)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return HTMLResponse(render_html_report(report, presentation))
