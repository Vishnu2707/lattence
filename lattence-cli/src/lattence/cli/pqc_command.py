import sys
from pathlib import Path
from typing import Annotated

import typer

from .crypto_workflow import create_crypto_assessment, crypto_assessment_json
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
from .presentation import render_crypto_assessment
from .workflow import exceeds_gate, write_report_artifacts

PathArgument = Annotated[Path, typer.Argument()]


def pqc_assess(
    path: PathArgument = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    del offline, planner
    assessment = create_crypto_assessment(path, output=out)
    write_report_artifacts(assessment.report, out)
    if json_output:
        typer.echo(crypto_assessment_json(assessment), nl=False)
    elif not quiet:
        typer.echo(
            render_crypto_assessment(
                assessment,
                path,
                command_name="pqc assess",
                color=not no_color and sys.stdout.isatty(),
            ),
            nl=False,
        )
    if exceeds_gate(assessment.report.summary, fail_on):
        raise typer.Exit(code=1)
