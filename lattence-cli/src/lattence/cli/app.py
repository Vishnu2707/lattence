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

app = typer.Typer(
    name="lattence",
    no_args_is_help=True,
    invoke_without_command=True,
    rich_markup_mode=None,
)
pqc_app = typer.Typer(name="pqc", no_args_is_help=True)
crypto_app = typer.Typer(name="crypto", no_args_is_help=True)
provider_app = typer.Typer(name="provider", no_args_is_help=True)
graph_app = typer.Typer(name="graph", no_args_is_help=True)
policy_app = typer.Typer(name="policy", no_args_is_help=True)


def _pending(command: str) -> None:
    typer.echo(f"{command}: command scaffold only", err=True)
    raise typer.Exit(code=3)


def _options(
    json_output: bool,
    out: Path,
    offline: bool,
    no_color: bool,
    quiet: bool,
    planner: Planner,
    fail_on: SeverityGate,
) -> None:
    del json_output, out, offline, no_color, quiet, planner, fail_on


@app.callback()
def root(
    version: Annotated[
        bool | None,
        typer.Option("--version", help="Show version and exit.", is_eager=True),
    ] = None,
) -> None:
    if version:
        typer.echo("lattence 0.0.0")
        raise typer.Exit()


@app.command()
def scan(
    path: Path = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _options(json_output, out, offline, no_color, quiet, planner, fail_on)
    _pending(f"scan {path}")


@app.command()
def attack(
    path: Path = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _options(json_output, out, offline, no_color, quiet, planner, fail_on)
    _pending(f"attack {path}")


@app.command()
def harden(
    path: Path = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _options(json_output, out, offline, no_color, quiet, planner, fail_on)
    _pending(f"harden {path}")


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
    _options(json_output, out, offline, no_color, quiet, planner, fail_on)
    _pending(f"verify {finding_id}")


@app.command()
def report(
    input_path: Path = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _options(json_output, out, offline, no_color, quiet, planner, fail_on)
    _pending(f"report {input_path}")


@app.command()
def tui(
    input_path: Path = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _options(json_output, out, offline, no_color, quiet, planner, fail_on)
    _pending(f"tui {input_path}")


def _path_command(command: str, path: Path, options: tuple[object, ...]) -> None:
    _options(*options)  # type: ignore[arg-type]
    _pending(f"{command} {path}")


@pqc_app.command("assess")
def pqc_assess(
    path: Path = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _path_command(
        "pqc assess",
        path,
        (json_output, out, offline, no_color, quiet, planner, fail_on),
    )


@crypto_app.command("chaos")
def crypto_chaos(
    path: Path = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _path_command(
        "crypto chaos",
        path,
        (json_output, out, offline, no_color, quiet, planner, fail_on),
    )


def _named_command(
    command: str,
    name: str,
    json_output: bool,
    out: Path,
    offline: bool,
    no_color: bool,
    quiet: bool,
    planner: Planner,
    fail_on: SeverityGate,
) -> None:
    _options(json_output, out, offline, no_color, quiet, planner, fail_on)
    _pending(f"{command} {name}")


@provider_app.command("enable")
def provider_enable(
    name: str,
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _named_command(
        "provider enable",
        name,
        json_output,
        out,
        offline,
        no_color,
        quiet,
        planner,
        fail_on,
    )


@provider_app.command("list")
def provider_list(
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _options(json_output, out, offline, no_color, quiet, planner, fail_on)
    _pending("provider list")


@graph_app.command("export")
def graph_export(
    input_path: Path = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _path_command(
        "graph export",
        input_path,
        (json_output, out, offline, no_color, quiet, planner, fail_on),
    )


@policy_app.command("check")
def policy_check(
    input_path: Path = Path("."),
    json_output: JsonOption = False,
    out: OutOption = Path("."),
    offline: OfflineOption = False,
    no_color: NoColorOption = False,
    quiet: QuietOption = False,
    planner: PlannerOption = Planner.RULES,
    fail_on: FailOnOption = SeverityGate.HIGH,
) -> None:
    _path_command(
        "policy check",
        input_path,
        (json_output, out, offline, no_color, quiet, planner, fail_on),
    )


app.add_typer(pqc_app, name="pqc")
app.add_typer(crypto_app, name="crypto")
app.add_typer(provider_app, name="provider")
app.add_typer(graph_app, name="graph")
app.add_typer(policy_app, name="policy")
