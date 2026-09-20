from pathlib import Path

import jsonschema
from fastapi import APIRouter, HTTPException
from lattence.cli import TargetDeclarationError, load_target_declaration
from lattence.cli.workflow import create_attack_report, machine_report
from lattence.evidence import Report

router = APIRouter()


@router.post("/v1/attack", response_model=Report)
def attack(path: str = ".", offline: bool = False) -> Report:
    target = Path(path)
    try:
        load_target_declaration(target)
    except TargetDeclarationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    try:
        report = create_attack_report(target, target, offline, target)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    try:
        machine_report(report)
    except jsonschema.ValidationError as error:
        raise HTTPException(
            status_code=500, detail=f"report failed schema validation: {error.message}"
        ) from error
    return report
