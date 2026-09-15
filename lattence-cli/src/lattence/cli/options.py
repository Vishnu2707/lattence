from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer


class Planner(StrEnum):
    RULES = "rules"
    LLM = "llm"


class SeverityGate(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    NONE = "none"


def require_implemented_planner(value: Planner) -> Planner:
    if value is Planner.LLM:
        raise typer.BadParameter(
            "LLM planner is not implemented; use --planner rules"
        )
    return value


JsonOption = Annotated[bool, typer.Option("--json", help="Write JSON to stdout.")]
OutOption = Annotated[Path, typer.Option("--out", help="Output path.")]
OfflineOption = Annotated[
    bool, typer.Option("--offline", help="Disable network access.")
]
NoColorOption = Annotated[
    bool, typer.Option("--no-color", help="Disable terminal colors.")
]
QuietOption = Annotated[bool, typer.Option("--quiet", help="Suppress normal logs.")]
PlannerOption = Annotated[
    Planner,
    typer.Option(
        "--planner", help="Planner mode.", callback=require_implemented_planner
    ),
]
FailOnOption = Annotated[
    SeverityGate, typer.Option("--fail-on", help="Finding failure threshold.")
]


@dataclass(frozen=True)
class CommonOptions:
    json_output: bool
    out: Path
    offline: bool
    no_color: bool
    quiet: bool
    planner: Planner
    fail_on: SeverityGate
