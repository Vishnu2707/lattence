import json
from pathlib import Path
from typing import Annotated

import typer

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
from .policy import ScopeCheck, ScopeValidationError, check_report_scope
from .targets import (
    TARGET_DECLARATION_NAME,
    TargetDeclarationError,
    load_scope_declaration,
)
from .workflow import load_report

policy_app = typer.Typer(name="policy", no_args_is_help=True)
PathArgument = Annotated[Path, typer.Argument()]
ScopeOption = Annotated[
    Path | None,
    typer.Option("--scope", help="Declared-scope YAML file."),
]


def _text(result: ScopeCheck) -> str:
    outcome = "PASS" if result.allowed else "FAIL"
    lines = [f"{outcome}  policy.scope  touched={len(result.touched_node_ids)}"]
    lines.extend(f"OUT-OF-SCOPE  {node_id}" for node_id in result.out_of_scope_node_ids)
    return "\n".join(lines) + "\n"


def _json(result: ScopeCheck) -> str:
    return (
        json.dumps(
            {
                "allowed": result.allowed,
                "out_of_scope_node_ids": result.out_of_scope_node_ids,
                "touched_node_ids": result.touched_node_ids,
            },
            sort_keys=True,
        )
        + "\n"
    )


@policy_app.command("check")
def policy_check(
    input_path: PathArgument = Path("."),
    scope: ScopeOption = None,
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    del out, offline, no_color, planner, fail_on
    try:
        report = load_report(input_path)
        report_directory = input_path if input_path.is_dir() else input_path.parent
        declaration_path = (
            scope
            if scope is not None
            else report_directory / report.project.root / TARGET_DECLARATION_NAME
        )
        declaration = load_scope_declaration(declaration_path)
        result = check_report_scope(report, declaration)
    except (OSError, ScopeValidationError, TargetDeclarationError, ValueError) as error:
        raise typer.BadParameter(str(error)) from error
    if json_output:
        typer.echo(_json(result), nl=False)
    elif not quiet:
        typer.echo(_text(result), nl=False)
    if not result.allowed:
        raise typer.Exit(code=1)
