from pathlib import Path
from typing import Annotated

import jsonschema
from fastapi import APIRouter, Depends, HTTPException
from lattence.cli.workflow import create_report, machine_report
from lattence.evidence import Report
from lattence.governance import Role

from ..auth import AuthenticatedCaller, require_access

router = APIRouter()


@router.get("/v1/scan", response_model=Report)
def scan(
    caller: Annotated[AuthenticatedCaller, Depends(require_access(Role.RUN_SCANS))],
    path: str = ".",
) -> Report:
    del caller
    try:
        report = create_report(Path(path))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    try:
        machine_report(report)
    except jsonschema.ValidationError as error:
        raise HTTPException(
            status_code=500, detail=f"report failed schema validation: {error.message}"
        ) from error
    return report
