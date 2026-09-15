import json
import shlex
from pathlib import Path
from typing import Annotated

import typer
from lattence.evidence import RemediationError, RemediationPlan, remediation_plans

from .options import (
    FailOnOption,
    JsonOption,
    NoColorOption,
    OfflineOption,
    OutOption,
    Planner,
    PlannerOption,
    QuietOption,
    SeverityGate,
)
from .workflow import load_report, severity_meets_gate


def _text(plans: tuple[RemediationPlan, ...]) -> str:
    lines: list[str] = []
    for plan in plans:
        if lines:
            lines.append("")
        lines.extend(
            (
                f"REMEDIATION  {plan.finding_id}  {plan.title}",
                (
                    f"Target       {plan.target.id}  {plan.target.type}  "
                    f"{plan.target.name}"
                ),
                f"Action       {plan.remediation}",
                f"Evidence     {plan.evidence_id}",
                f"Reproduce    {shlex.join(plan.reproduction.command)}",
                f"Working dir  {plan.reproduction.working_directory}",
                f"Expected     {plan.reproduction.expected}",
            )
        )
    return "\n".join(lines) + ("\n" if lines else "")


def _json(plans: tuple[RemediationPlan, ...]) -> str:
    payload = {"plans": [plan.model_dump(mode="json") for plan in plans]}
    return json.dumps(payload, sort_keys=True) + "\n"


def harden(
    input_value: Annotated[str, typer.Argument()] = ".",
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    del offline, no_color, planner
    finding_id = input_value if input_value.startswith("LT-") else None
    report_path = out if finding_id is not None else Path(input_value)
    try:
        plans = remediation_plans(load_report(report_path), finding_id)
    except (OSError, RemediationError, ValueError) as error:
        raise typer.BadParameter(str(error)) from error
    if json_output:
        typer.echo(_json(plans), nl=False)
    elif not quiet:
        typer.echo(_text(plans), nl=False)
    if any(severity_meets_gate(plan.severity, fail_on) for plan in plans):
        raise typer.Exit(code=1)
