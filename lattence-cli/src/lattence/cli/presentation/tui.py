import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, cast

from lattence.evidence import SecurityPresentation
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def load_visual_grammar() -> dict[str, Any]:
    current = Path(__file__).resolve()
    candidates = [
        current.parents[2] / "assets" / "visual-grammar.json",
        *(
            parent / "lattence-ui" / "src" / "visual-grammar.json"
            for parent in current.parents
        ),
    ]
    grammar_path = next((path for path in candidates if path.is_file()), None)
    if grammar_path is None:
        raise RuntimeError("cannot locate shared visual grammar")
    return cast(dict[str, Any], json.loads(grammar_path.read_text(encoding="utf-8")))


@dataclass(frozen=True)
class TuiState:
    section_index: int = 0
    row_index: int = 0
    detail_open: bool = False
    path_hop_index: int = 0
    help_open: bool = False
    quit_requested: bool = False


def handle_tui_key(
    state: TuiState, key: str, row_count: int, *, hop_count: int = 0
) -> TuiState:
    navigation_count = len(load_visual_grammar()["navigation"])
    if key in {"q", "Q"}:
        return replace(state, quit_requested=True)
    if key == "?":
        return replace(state, help_open=not state.help_open)
    if key in {"escape", "esc"}:
        return replace(state, help_open=False, detail_open=False)
    if key == "[" and hop_count:
        return replace(
            state, path_hop_index=(state.path_hop_index - 1) % hop_count
        )
    if key == "]" and hop_count:
        return replace(
            state, path_hop_index=(state.path_hop_index + 1) % hop_count
        )
    if key in {"left", "h", "shift+tab"}:
        return replace(
            state,
            section_index=(state.section_index - 1) % navigation_count,
            row_index=0,
            detail_open=False,
            path_hop_index=0,
        )
    if key in {"right", "l", "tab"}:
        return replace(
            state,
            section_index=(state.section_index + 1) % navigation_count,
            row_index=0,
            detail_open=False,
            path_hop_index=0,
        )
    if key in {"up", "k"} and row_count:
        return replace(
            state,
            row_index=(state.row_index - 1) % row_count,
            path_hop_index=0,
        )
    if key in {"down", "j"} and row_count:
        return replace(
            state,
            row_index=(state.row_index + 1) % row_count,
            path_hop_index=0,
        )
    if key in {"enter", "return"} and row_count:
        return replace(state, detail_open=True, path_hop_index=0)
    return state


def _rows(presentation: SecurityPresentation, section: str) -> list[dict[str, str]]:
    if section == "Attack Graph":
        return [
            {
                "kind": "CHAIN",
                "id": chain.id,
                "state": f"{len(chain.hops)} hops",
                "detail": chain.explanation,
            }
            for chain in presentation.cross_layer_chains
        ]
    if section in {"Findings", "AI Security", "Agent Security", "MCP"}:
        prefix = {
            "AI Security": "LT-AI-",
            "Agent Security": "LT-AGENT-",
            "MCP": "LT-MCP-",
        }.get(section)
        return [
            {
                "kind": finding.severity.upper(),
                "id": finding.id,
                "state": finding.status.upper(),
                "detail": json.dumps(finding.model_dump(mode="json"), sort_keys=True),
            }
            for finding in presentation.findings
            if prefix is None or finding.id.startswith(prefix)
        ]
    node_type = {
        "Applications": "application",
        "Cryptography": "crypto_algorithm",
    }.get(section)
    nodes = (
        presentation.graph.nodes
        if node_type is None
        else [node for node in presentation.graph.nodes if node.type == node_type]
    )
    return [
        {
            "kind": node.type.upper(),
            "id": node.id,
            "state": "PASS",
            "detail": json.dumps(node.model_dump(mode="json"), sort_keys=True),
        }
        for node in nodes
    ]


def _navigation(state: TuiState, navigation: list[str]) -> Panel:
    lines = []
    for index, label in enumerate(navigation):
        marker = ">" if index == state.section_index else " "
        lines.append(
            Text(f"{marker} {label}", style="bold blue" if marker == ">" else "")
        )
    return Panel(Group(*lines), title="LATTENCE", border_style="bright_black")


def _table(rows: list[dict[str, str]], state: TuiState, section: str) -> Panel:
    table = Table(expand=True, box=None, pad_edge=False, header_style="bold")
    table.add_column("TYPE", width=13)
    table.add_column("IDENTIFIER", overflow="ellipsis")
    table.add_column("STATE", width=12)
    if not rows:
        table.add_row("", "No data. Run lattence scan .", "")
    for index, row in enumerate(rows):
        style = "reverse" if index == state.row_index else ""
        table.add_row(row["kind"], row["id"], row["state"], style=style)
    return Panel(table, title=section, border_style="bright_black")


def _chain_detail(chain: Any, selected_hop: int) -> Group:
    lines: list[Text] = [Text(chain.explanation), Text("")]
    for index, hop in enumerate(chain.hops):
        marker = ">" if index == selected_hop else " "
        heading = (
            f"{marker} HOP {index + 1}  {hop.edge_type.upper()}  "
            f"{hop.traversal.upper()}"
        )
        lines.append(Text(heading, style="reverse" if marker == ">" else ""))
        lines.append(Text(f"  {hop.from_node_id} -> {hop.to_node_id}"))
        lines.append(Text(f"  STORED {hop.source_id} -> {hop.target_id}"))
        for reference in hop.evidence_refs:
            lines.append(Text(f"  EVIDENCE {reference}"))
    for reference in chain.evidence_refs:
        lines.append(Text(f"CHAIN EVIDENCE {reference}"))
    return Group(*lines)


def render_tui(
    presentation: SecurityPresentation,
    state: TuiState | None = None,
    *,
    width: int = 120,
    height: int = 34,
    color: bool = False,
) -> str:
    state = state or TuiState()
    grammar = load_visual_grammar()
    navigation = list(grammar["navigation"])
    section = navigation[state.section_index]
    rows = _rows(presentation, section)
    selected_index = min(state.row_index, max(0, len(rows) - 1))

    layout = Layout()
    layout.split_column(Layout(name="body"), Layout(name="footer", size=1))
    layout["body"].split_row(
        Layout(_navigation(state, navigation), name="navigation", size=23),
        Layout(_table(rows, state, section), name="table"),
    )
    if state.detail_open and rows:
        detail_content: Any = rows[selected_index]["detail"]
        if section == "Attack Graph":
            chain = presentation.cross_layer_chains[selected_index]
            hop_index = min(state.path_hop_index, len(chain.hops) - 1)
            detail_content = _chain_detail(chain, hop_index)
        detail = Panel(
            detail_content,
            title="DETAIL",
            border_style="bright_black",
        )
        layout["body"].split_row(
            Layout(_navigation(state, navigation), size=23),
            Layout(_table(rows, state, section)),
            Layout(detail, size=38),
        )
    footer = "←/→ section  ↑/↓ row  Enter detail  [/] hop  ? help  q quit"
    if state.help_open:
        footer = "HELP  Tab sections  j/k rows  Enter detail  Esc close  q quit"
    layout["footer"].update(Text(footer, style="dim"))

    console = Console(
        record=True,
        width=width,
        height=height,
        force_terminal=color,
        color_system="truecolor" if color else None,
    )
    console.print(layout)
    return console.export_text(styles=color)
