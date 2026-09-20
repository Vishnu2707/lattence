from lattence.graph import Node
from pydantic import BaseModel, ConfigDict

from .models import ReproductionRecipe, Severity
from .reporting import Report


class RemediationError(ValueError):
    pass


class RemediationPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    finding_id: str
    title: str
    severity: Severity
    remediation: str
    target: Node
    evidence_id: str
    reproduction: ReproductionRecipe


def remediation_plans(
    report: Report, finding_id: str | None = None
) -> tuple[RemediationPlan, ...]:
    findings = report.findings
    if finding_id is not None:
        findings = [finding for finding in findings if finding.id == finding_id]
        if not findings:
            raise RemediationError(f"finding not found: {finding_id}")
    nodes = {node.id: node for node in report.graph.nodes}
    plans: list[RemediationPlan] = []
    for finding in sorted(findings, key=lambda item: item.id):
        target = nodes.get(finding.target_node_id)
        if target is None:
            raise RemediationError(
                f"target node not found for {finding.id}: {finding.target_node_id}"
            )
        plans.append(
            RemediationPlan(
                finding_id=finding.id,
                title=finding.title,
                severity=finding.severity,
                remediation=finding.remediation,
                target=target,
                evidence_id=finding.evidence.id,
                reproduction=finding.reproduction,
            )
        )
    return tuple(plans)
