from collections import Counter
from pathlib import Path

from lattence.evidence import Report
from lattence.graph import CryptoAlgorithm, NodeType
from rich.console import Console
from rich.text import Text

_LABELS: dict[NodeType, str] = {
    "agent": "Agents",
    "mcp_server": "MCP servers",
    "tool": "Tools",
    "api": "External APIs",
    "database": "Data stores",
}
_SEVERITY_STYLE = {
    "critical": "#E5484D",
    "high": "#F76808",
    "medium": "#E2A336",
    "low": "#3E9B4F",
    "info": "#6E7A8A",
}


def _row(label: str, value: object, width: int = 22) -> str:
    return f"  {label:<{width}}{value}"


def _plain_summary(
    report: Report,
    target: Path,
    report_path: Path,
    elapsed_seconds: float,
) -> str:
    counts = Counter(node.type for node in report.graph.nodes)
    lines = [f"LATTENCE  scan  {target}", "", "DISCOVERY"]
    lines.extend(_row(label, counts[node_type]) for node_type, label in _LABELS.items())
    lines.extend(("", "AI ATTACK SURFACE"))
    if report.findings:
        lines.extend(
            _row(finding.title, finding.severity.upper())
            for finding in report.findings[:5]
        )
    else:
        lines.append(_row("Findings", "NONE"))

    algorithms = [
        node for node in report.graph.nodes if isinstance(node, CryptoAlgorithm)
    ]
    algorithm_counts = Counter(node.algorithm for node in algorithms)
    vulnerable = sum(node.quantum_status == "vulnerable" for node in algorithms)
    lines.extend(("", "CRYPTOGRAPHY"))
    lines.extend(_row(name, count) for name, count in sorted(algorithm_counts.items()))
    lines.append(_row("Quantum vulnerable", vulnerable))
    lines.append(_row("PQC readiness", f"{report.summary.pqc_readiness:g}%"))
    lines.extend(
        (
            "",
            _row("Attack paths", len(report.graph.edges), width=23),
            _row("Findings", report.summary.total, width=23),
            "",
            f"Report  {report_path}      Elapsed  {elapsed_seconds:.1f}s",
        )
    )
    return "\n".join(lines) + "\n"


def render_scan_summary(
    report: Report,
    target: Path,
    report_path: Path,
    elapsed_seconds: float,
    color: bool = False,
) -> str:
    plain = _plain_summary(report, target, report_path, elapsed_seconds)
    if not color:
        return plain
    console = Console(
        record=True, force_terminal=True, color_system="truecolor", width=100
    )
    for line in plain.rstrip().splitlines():
        text = Text(line)
        if line in {"DISCOVERY", "AI ATTACK SURFACE", "CRYPTOGRAPHY"}:
            text.stylize("bold #4C8DFF")
        for severity, style in _SEVERITY_STYLE.items():
            if line.endswith(severity.upper()):
                text.stylize(style)
        console.print(text)
    return console.export_text(styles=True)
