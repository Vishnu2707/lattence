import hashlib
import json
from datetime import datetime

from lattence.discovery import RulePack
from lattence.graph import NodeId

from .models import (
    EnvironmentFingerprint,
    EvidenceBundle,
    EvidenceInput,
    Finding,
    PolicyDecision,
    ReproductionRecipe,
)


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def normalize_rule_finding(
    rule: RulePack,
    target_node_id: NodeId,
    observed_at: datetime,
    replay_seed: int,
    working_directory: str = ".",
    tool_version: str = "0.0.0",
) -> Finding:
    evidence_id = f"evidence:{rule.id}:{target_node_id}"
    evidence = EvidenceBundle(
        id=evidence_id,
        inputs=[
            EvidenceInput(
                name="attack-rule",
                media_type="application/json",
                sha256=_digest({"rule_id": rule.id, "target": target_node_id}),
                value={"rule_id": rule.id},
            )
        ],
        transcript=[],
        telemetry_spans=[],
        policy_decision=PolicyDecision(
            policy_id=rule.id,
            outcome="fail",
            reason=rule.finding.message,
            facts={"target_node_id": target_node_id},
        ),
        started_at=observed_at,
        finished_at=observed_at,
        environment=EnvironmentFingerprint(
            platform="offline",
            python="unknown",
            lattence_version=tool_version,
            dependency_digest=_digest([]),
            configuration_digest=_digest({"planner": "rules", "offline": True}),
        ),
        replay_seed=replay_seed,
    )
    return Finding(
        id=rule.id,
        title=rule.title,
        source="native-rule",
        severity=rule.severity,
        confidence=rule.confidence,
        owasp_llm=sorted(rule.finding.owasp_llm),
        owasp_agentic=sorted(rule.finding.owasp_agentic),
        cwe=sorted(rule.finding.cwe),
        target_node_id=target_node_id,
        evidence=evidence,
        reproduction=ReproductionRecipe(
            command=["lattence", "attack", "--offline"],
            working_directory=working_directory,
            expected=rule.finding.message,
        ),
        remediation=rule.finding.remediation,
    )
