import getpass
import json
from dataclasses import dataclass
from pathlib import Path

from lattence.evidence import Report, ReportSummary
from lattence.graph import CryptoAlgorithm, JsonValue
from lattence_ai.attacks import (
    VerificationOutcome,
    load_native_attack_catalog,
    verify_finding,
)

from .artifact_workflow import load_report
from .options import SeverityGate
from .report_workflow import data_root

_SEVERITY_ORDER = ("critical", "high", "medium", "low", "info")


def exceeds_gate(summary: ReportSummary, gate: SeverityGate) -> bool:
    if gate == SeverityGate.NONE:
        return False
    index = _SEVERITY_ORDER.index(gate.value)
    return any(getattr(summary, level) > 0 for level in _SEVERITY_ORDER[: index + 1])


def severity_meets_gate(severity: str, gate: SeverityGate) -> bool:
    if gate == SeverityGate.NONE:
        return False
    return _SEVERITY_ORDER.index(severity) <= _SEVERITY_ORDER.index(gate.value)


def attack_text(report: Report, target: Path) -> str:
    lines = [f"LATTENCE  attack  {target}", ""]
    for finding in report.findings:
        lines.append(
            f"VULNERABLE  {finding.id}  {finding.title}  {finding.target_node_id}"
        )
    indirect = next((item for item in report.findings if item.id == "LT-AI-002"), None)
    tool = next(
        (
            node
            for node in report.graph.nodes
            if node.type == "tool" and node.server_id is not None
        ),
        None,
    )
    if indirect is not None and tool is not None:
        lines.extend(("", f"Indirect chain  {indirect.target_node_id} -> {tool.id}"))
    lines.extend(("", f"Findings  {report.summary.total}"))
    return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class VerificationResult:
    outcome: VerificationOutcome
    finding_id: str
    title: str | None
    target_node_id: str | None
    severity: str | None


def verify_report(report_path: Path, finding_id: str) -> VerificationResult:
    report = load_report(report_path)
    rules = load_native_attack_catalog(data_root() / "attacks").rules
    outcome = verify_finding(report, finding_id, rules)
    finding = next((item for item in report.findings if item.id == finding_id), None)
    return VerificationResult(
        outcome,
        finding_id,
        finding.title if finding else None,
        finding.target_node_id if finding else None,
        finding.severity if finding else None,
    )


def verify_text(result: VerificationResult) -> str:
    if result.outcome is VerificationOutcome.NOT_FOUND:
        return f"BLOCKED  {result.finding_id}  finding not found\n"
    word = "VULNERABLE" if result.outcome is VerificationOutcome.VULNERABLE else "PASS"
    return f"{word}  {result.finding_id}  {result.title}  {result.target_node_id}\n"


def verify_json(result: VerificationResult) -> str:
    payload = {
        "finding_id": result.finding_id,
        "outcome": result.outcome.value,
        "severity": result.severity,
        "target_node_id": result.target_node_id,
        "title": result.title,
    }
    return json.dumps(payload, sort_keys=True) + "\n"


def readiness_json(report: Report) -> str:
    algorithms = [
        node for node in report.graph.nodes if isinstance(node, CryptoAlgorithm)
    ]
    payload = {
        "algorithms": len(algorithms),
        "pqc_readiness": report.summary.pqc_readiness,
        "quantum_vulnerable": sum(
            node.quantum_status == "vulnerable" for node in algorithms
        ),
    }
    return json.dumps(payload, sort_keys=True) + "\n"


def record_cli_audit_event(
    *, action: str, target: Path, result: str, out: Path, details: dict[str, JsonValue]
) -> None:
    from lattence.governance import AuditLog, default_audit_db_path

    log = AuditLog(default_audit_db_path(out))
    try:
        actor = getpass.getuser()
    except OSError:
        actor = "unknown"
    log.record(
        actor=actor, action=action, target=str(target), result=result, details=details
    )
