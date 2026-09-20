from pathlib import Path

from fastapi import APIRouter, HTTPException
from lattence.cli.workflow import create_report
from lattence.evidence import Report

router = APIRouter()


@router.get("/v1/scan", response_model=Report)
def scan(path: str = ".") -> Report:
    try:
        return create_report(Path(path))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
