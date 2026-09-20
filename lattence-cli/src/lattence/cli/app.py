import sys
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Annotated

import typer
from lattence_ai.attacks import VerificationOutcome

from .crypto_command import crypto_chaos
from .graph_chain_command import graph_chain
from .harden_command import harden
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
from .policy_command import policy_app
from .pqc_command import pqc_assess
from .presentation import (
    render_attack_summary,
    render_banner,
    render_scan_summary,
    render_tui,
    run_tui,
)
from .presentation_workflow import (
    create_security_presentation,
    write_dashboard_data,
)
from .provider_commands import provider_app
from .rbac_commands import rbac_app
from .serve_command import serve
from .targets import TargetDeclarationError, load_target_declaration
from .workflow import (
    attack_text,
    create_attack_report,
    create_report,
    exceeds_gate,
    load_report,
    machine_report,
    record_cli_audit_event,
    severity_meets_gate,
    verify_json,
    verify_report,
    verify_text,
    write_graph,
    write_report_artifacts,
    write_sarif,
)

app = typer.Typer(
    name="lattence",
    invoke_without_command=True,
    rich_markup_mode=None,
)
pqc_app = typer.Typer(name="pqc", no_args_is_help=True)
crypto_app = typer.Typer(name="crypto", no_args_is_help=True)
graph_app = typer.Typer(name="graph", no_args_is_help=True)
PathArgument = Annotated[Path, typer.Argument()]


@app.callback()
def root(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option("--version", help="Show version and exit.", is_eager=True),
    ] = None,
) -> None:
    if version:
        typer.echo(render_banner())
        typer.echo(f"lattence {package_version('lattence')}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(render_banner())
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def scan(
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
    result = create_report(path, out)
    artifacts = write_report_artifacts(result, out)
    record_cli_audit_event(
        action="scan",
        target=path,
        result="completed",
        out=out,
        details={"findings": result.summary.total},
    )
    if json_output:
        typer.echo(machine_report(result), nl=False)
    elif not quiet:
        typer.echo(
            render_scan_summary(
                result,
                path,
                artifacts.html,
                0.0,
                color=not no_color and sys.stdout.isatty(),
            ),
            nl=False,
        )
    if exceeds_gate(result.summary, fail_on):
        raise typer.Exit(code=1)


@app.command()
def attack(
    path: PathArgument = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    del planner
    try:
        load_target_declaration(path)
    except TargetDeclarationError as error:
        raise typer.BadParameter(str(error)) from error
    provider_directory = out.parent if out.suffix else out
    result = create_attack_report(path, provider_directory, offline, out)
    write_report_artifacts(result, out)
    record_cli_audit_event(
        action="attack",
        target=path,
        result="completed",
        out=out,
        details={"findings": result.summary.total},
    )
    if json_output:
        typer.echo(machine_report(result), nl=False)
    elif not quiet:
        typer.echo(
            render_attack_summary(
                attack_text(result, path),
                color=not no_color and sys.stdout.isatty(),
            ),
            nl=False,
        )
    if exceeds_gate(result.summary, fail_on):
        raise typer.Exit(code=1)


@app.command()
def verify(
    finding_id: str,
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    del offline, no_color, planner
    result = verify_report(out, finding_id)
    if json_output:
        typer.echo(verify_json(result), nl=False)
    elif not quiet:
        typer.echo(verify_text(result), nl=False)
    if result.outcome is VerificationOutcome.NOT_FOUND:
        raise typer.Exit(code=2)
    if result.outcome is VerificationOutcome.VULNERABLE and (
        result.severity is not None and severity_meets_gate(result.severity, fail_on)
    ):
        raise typer.Exit(code=1)


@app.command()
def report(
    input_path: PathArgument = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    del offline, no_color, planner, fail_on
    result = load_report(input_path)
    artifacts = write_report_artifacts(result, out)
    if json_output:
        typer.echo(machine_report(result), nl=False)
    elif not quiet:
        typer.echo(f"Report  {artifacts.html}")


@app.command()
def sarif(
    input_path: PathArgument = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    del offline, no_color, planner, fail_on
    result = load_report(input_path)
    if json_output:
        from lattence.evidence import sarif_json

        typer.echo(sarif_json(result), nl=False)
    else:
        destination = write_sarif(result, out)
        if not quiet:
            typer.echo(f"SARIF  {destination}")


@app.command()
def tui(
    input_path: PathArgument = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    del offline, planner, fail_on
    if not json_output and not quiet:
        typer.echo(render_banner())
    presentation = create_security_presentation(input_path, out)
    write_dashboard_data(presentation, out)
    if json_output:
        from lattence.evidence import presentation_json

        typer.echo(presentation_json(presentation), nl=False)
    elif not quiet:
        interactive = sys.stdin.isatty() and sys.stdout.isatty()
        if interactive:
            run_tui(presentation, color=not no_color)
        else:
            typer.echo(render_tui(presentation, color=False), nl=False)


@graph_app.command("export")
def graph_export(
    input_path: PathArgument = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    del offline, no_color, planner, fail_on
    result = create_report(input_path, out)
    if json_output:
        from lattence.graph import security_graph_json

        typer.echo(security_graph_json(result.graph), nl=False)
    else:
        destination = write_graph(result, out)
        if not quiet:
            typer.echo(f"Graph  {destination}")


app.add_typer(pqc_app, name="pqc")
app.add_typer(crypto_app, name="crypto")
app.add_typer(provider_app, name="provider")
app.add_typer(graph_app, name="graph")
app.add_typer(policy_app, name="policy")
app.add_typer(rbac_app, name="rbac")
app.command("harden")(harden)
app.command("serve")(serve)
pqc_app.command("assess")(pqc_assess)
crypto_app.command("chaos")(crypto_chaos)
graph_app.command("chain")(graph_chain)
