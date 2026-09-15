import json
from pathlib import Path

import typer
from lattence.providers import ProviderRegistryError, enable_provider, list_providers

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

provider_app = typer.Typer(name="provider", no_args_is_help=True)


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
    del offline, no_color, planner, fail_on
    try:
        state = enable_provider(name, out)
    except ProviderRegistryError as error:
        raise typer.BadParameter(str(error)) from error
    if json_output:
        typer.echo(json.dumps(state.as_json(), sort_keys=True))
    elif not quiet:
        availability = "available" if state.available else "unavailable"
        typer.echo(f"{state.name} enabled {availability}")


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
    del offline, no_color, planner, fail_on
    try:
        states = list_providers(out)
    except ProviderRegistryError as error:
        raise typer.BadParameter(str(error)) from error
    if json_output:
        typer.echo(
            json.dumps(
                {"providers": [state.as_json() for state in states]}, sort_keys=True
            )
        )
    elif not quiet:
        for state in states:
            enabled = "enabled" if state.enabled else "disabled"
            available = "available" if state.available else "unavailable"
            typer.echo(f"{state.name:<10} {enabled:<8}  {available}")
