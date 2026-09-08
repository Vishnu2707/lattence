from pathlib import Path

import typer

from .options import Planner, SeverityGate


def pending(command: str) -> None:
    typer.echo(f"{command}: command scaffold only", err=True)
    raise typer.Exit(code=3)


def common_options(
    json_output: bool,
    out: Path,
    offline: bool,
    no_color: bool,
    quiet: bool,
    planner: Planner,
    fail_on: SeverityGate,
) -> None:
    del json_output, out, offline, no_color, quiet, planner, fail_on


def path_command(command: str, path: Path, options: tuple[object, ...]) -> None:
    common_options(*options)  # type: ignore[arg-type]
    pending(f"{command} {path}")


def named_command(
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
    common_options(json_output, out, offline, no_color, quiet, planner, fail_on)
    pending(f"{command} {name}")
