from pathlib import Path

from rich.console import Console
from rich.text import Text

from ..crypto_workflow import CryptoAssessment

_HEADINGS = {
    "CRYPTO GRAPH",
    "DOWNGRADE VALIDATION",
    "HYBRID TLS",
    "MIGRATION TESTS",
    "CRYPTO AGILITY",
}
_STATUS_STYLE = {
    "ALREADY_MIGRATED": "#3E9B4F",
    "BLOCKED": "#E2A336",
    "DIRECT_READY": "#4C8DFF",
    "HYBRID_READY": "#4C8DFF",
    "INVALID": "#E5484D",
    "PARTIAL": "#E2A336",
    "RESISTANT": "#3E9B4F",
    "VALID": "#3E9B4F",
    "VULNERABLE": "#E5484D",
}


def _row(label: str, value: object) -> str:
    return f"  {label:<24}{value}"


def _plain_crypto(assessment: CryptoAssessment, target: Path) -> str:
    lines = [f"LATTENCE  crypto  {target}", "", "CRYPTO GRAPH"]
    lines.extend(
        (
            _row("Nodes", len(assessment.crypto_graph.nodes)),
            _row("Relationships", len(assessment.crypto_graph.edges)),
            _row("Vulnerable paths", len(assessment.vulnerable_paths)),
        )
    )
    for node in assessment.crypto_graph.nodes[:8]:
        status = f" [{node.quantum_status}]" if node.quantum_status else ""
        lines.append(_row(node.kind, f"{node.name}{status}"))
    lines.extend(
        (
            "",
            "MIGRATION TESTS",
            _row("ML-KEM", assessment.ml_kem.status.upper()),
            _row("ML-DSA", assessment.ml_dsa.status.upper()),
            "",
            "HYBRID TLS",
            _row("Validation", assessment.hybrid_tls.status.upper()),
            _row("Key exchange", assessment.hybrid_tls.hybrid_key_exchange),
            _row("Signatures", assessment.hybrid_tls.hybrid_signature),
            "",
            "CRYPTO AGILITY",
            _row("Score", f"{assessment.agility.percentage}%"),
        )
    )
    lines.extend(
        _row(component.name.replace("_", " ").title(), f"{component.score}%")
        for component in assessment.agility.components
    )
    lines.extend(
        (
            "",
            "DOWNGRADE VALIDATION",
            _row("Status", assessment.downgrade.status.upper()),
            _row("Experiments", len(assessment.downgrade.evidence)),
            _row("Findings", assessment.report.summary.total),
        )
    )
    return "\n".join(lines) + "\n"


def render_crypto_assessment(
    assessment: CryptoAssessment,
    target: Path,
    *,
    color: bool = False,
) -> str:
    plain = _plain_crypto(assessment, target)
    if not color:
        return plain
    console = Console(
        record=True, force_terminal=True, color_system="truecolor", width=100
    )
    for line in plain.rstrip().splitlines():
        text = Text(line)
        if line in _HEADINGS:
            text.stylize("bold #4C8DFF")
        else:
            for status, style in _STATUS_STYLE.items():
                if line.endswith(status):
                    text.stylize(style)
        console.print(text)
    return console.export_text(styles=True)
