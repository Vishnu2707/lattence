from pathlib import Path
from typing import Annotated

import typer
from lattence_crypto.chaos import UnsafeCryptoMutation

from .crypto_workflow import (
    CryptoWorkflowError,
    crypto_assessment_json,
    run_crypto_chaos,
)
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
from .targets import TargetDeclarationError, load_target_declaration
from .workflow import exceeds_gate, write_report_artifacts

PathArgument = Annotated[Path, typer.Argument()]


def crypto_chaos(
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
    try:
        declaration = load_target_declaration(path)
        declared_paths = tuple(
            target.value
            for target in declaration.targets
            if target.kind == "project" and target.value not in {".", "./"}
        )
        if not declared_paths:
            raise CryptoWorkflowError(
                "crypto chaos requires an explicitly declared configuration file"
            )
        assessment = run_crypto_chaos(path, declared_paths)
    except (CryptoWorkflowError, TargetDeclarationError, UnsafeCryptoMutation) as error:
        raise typer.BadParameter(str(error)) from error
    write_report_artifacts(assessment.report, out)
    if json_output:
        typer.echo(crypto_assessment_json(assessment), nl=False)
    elif not quiet:
        typer.echo(
            f"Crypto chaos  {assessment.downgrade.status}\n"
            f"Experiments  {len(assessment.downgrade.evidence)}\n"
            "Rollback  verified"
        )
    if exceeds_gate(assessment.report.summary, fail_on):
        raise typer.Exit(code=1)
