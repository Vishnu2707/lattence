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
    del offline, no_color, planner
    assessment = create_crypto_assessment(path)
    write_report_artifacts(assessment.report, out)
    if json_output:
        typer.echo(crypto_assessment_json(assessment), nl=False)
    elif not quiet:
        typer.echo(
            f"PQC readiness  {assessment.report.summary.pqc_readiness:g}%\n"
            f"Crypto agility  {assessment.agility.percentage}%\n"
            f"ML-KEM  {assessment.ml_kem.status}\n"
            f"ML-DSA  {assessment.ml_dsa.status}\n"
            f"Hybrid TLS  {assessment.hybrid_tls.status}"
        )
    if exceeds_gate(assessment.report.summary, fail_on):
        raise typer.Exit(code=1)
