from pathlib import Path
from typing import Annotated

import jsonschema
from fastapi import APIRouter, Depends, HTTPException
from lattence.cli import TargetDeclarationError, load_target_declaration
from lattence.cli.workflow import create_attack_report, machine_report
from lattence.evidence import Report
from lattence.governance import Role

from ..audit import record_api_audit_event
from ..auth import AuthenticatedCaller, require_access

router = APIRouter()


@router.post("/v1/attack", response_model=Report)
def attack(
    caller: Annotated[AuthenticatedCaller, Depends(require_access(Role.RUN_ATTACKS))],
    path: str = ".",
    offline: bool = False,
) -> Report:
    target = Path(path)
    try:
        load_target_declaration(target)
    except TargetDeclarationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    try:
        report = create_attack_report(target, target, offline, target)
    except FileNotFoundError as error:
        record_api_audit_event(
            caller_id=caller.caller_id,
            action="attack",
            target=path,
            result="not_found",
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    try:
        machine_report(report)
    except jsonschema.ValidationError as error:
        raise HTTPException(
            status_code=500, detail=f"report failed schema validation: {error.message}"
        ) from error
    record_api_audit_event(
        caller_id=caller.caller_id,
        action="attack",
        target=path,
        result="completed",
        details={"findings": report.summary.total},
    )
    return report
