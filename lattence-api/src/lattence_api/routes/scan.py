from pathlib import Path

import jsonschema
from fastapi import APIRouter, HTTPException
from lattence.cli.workflow import create_report, machine_report
from lattence.evidence import Report

router = APIRouter()


@router.get("/v1/scan", response_model=Report)
def scan(path: str = ".") -> Report:
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
