import io
import sys
from pathlib import Path
from typing import Annotated

import typer
from lattence.evidence import SecurityPresentation, presentation_json
from rich.console import Console
from rich.text import Text

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
from .presentation_workflow import (
    create_security_presentation,
    write_dashboard_data,
)

PathArgument = Annotated[Path, typer.Argument()]


def _chain_lines(presentation: SecurityPresentation, project: Path) -> list[Text]:
    chains = presentation.cross_layer_chains
    lines = [Text(f"LATTENCE  graph chain  {project}"), Text()]
    lines.append(Text(f"CROSS-LAYER CHAINS  {len(chains)}", style="bold #4C8DFF"))
    if not chains:
        lines.append(Text("PASS  No cross-layer finding chains."))
        return lines
    for index, chain in enumerate(chains, start=1):
        lines.extend(
            [
                Text(),
                Text(
                    f"VULNERABLE  {index}/{len(chains)}  "
                    f"{chain.source_finding_id} -> {chain.crypto_finding_id}",
                    style="bold #E5484D",
                ),
                Text(f"  START       {chain.start_node_id}"),
            ]
        )
        for hop_index, hop in enumerate(chain.hops, start=1):
            lines.append(
                Text(
                    f"  EDGE {hop_index:<2}     {hop.edge_type}  {hop.traversal}",
                    style="bold #4C8DFF",
                )
            )
            lines.append(Text(f"    STORED    {hop.source_id} -> {hop.target_id}"))
            lines.append(Text(f"    TRAVERSE  {hop.from_node_id} -> {hop.to_node_id}"))
            evidence = ", ".join(hop.evidence_refs) or "none"
            lines.append(Text(f"    EVIDENCE  {evidence}", style="#8A94A6"))
        lines.append(Text(f"  END         {chain.end_node_id}"))
        lines.append(
            Text(
                f"  EVIDENCE    {', '.join(chain.evidence_refs) or 'none'}",
                style="#8A94A6",
            )
        )
    return lines


def render_graph_chains(
    presentation: SecurityPresentation,
    project: Path,
    *,
    color: bool,
) -> str:
    stream = io.StringIO()
    console = Console(
        file=stream,
        force_terminal=color,
        color_system="truecolor" if color else None,
        width=160,
    )
    for line in _chain_lines(presentation, project):
        console.print(line)
    return stream.getvalue()


def graph_chain(
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
    presentation = create_security_presentation(input_path, out)
    write_dashboard_data(presentation, out)
    if json_output:
        typer.echo(presentation_json(presentation), nl=False)
    elif not quiet:
        typer.echo(
            render_graph_chains(
                presentation,
                input_path,
                color=not no_color and sys.stdout.isatty(),
            ),
            nl=False,
        )
