import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

from lattence.graph import JsonValue, NodeId
from lattence_crypto.agility import CryptoAgilityScore
from lattence_crypto.chaos import DowngradeValidation
from lattence_crypto.pqc import MLDSAMigration, MLKEMMigration

from .models import (
    EnvironmentFingerprint,
    EvidenceBundle,
    EvidenceInput,
    Finding,
    PolicyDecision,
    ReproductionRecipe,
    Severity,
)


@dataclass(frozen=True)
class CryptoFindingTargets:
    ml_kem: NodeId
    ml_dsa: NodeId
    agility: NodeId
    downgrade: NodeId


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _finding(
    *,
    finding_id: str,
    title: str,
    severity: Severity,
    target_node_id: NodeId,
    summary: dict[str, JsonValue],
    observed_at: datetime,
    remediation: str,
    command: list[str],
    tool_version: str,
) -> Finding:
    evidence_id = f"evidence:{finding_id}:{target_node_id}"
    evidence = EvidenceBundle(
        id=evidence_id,
        inputs=[
            EvidenceInput(
                name="crypto-assessment",
                media_type="application/json",
                sha256=_digest(summary),
                value=summary,
            )
        ],
        transcript=[],
        telemetry_spans=[],
        policy_decision=PolicyDecision(
            policy_id=finding_id,
            outcome="fail",
            reason=title,
            facts=summary,
        ),
        started_at=observed_at,
        finished_at=observed_at,
        environment=EnvironmentFingerprint(
            platform="offline",
            python="unknown",
            lattence_version=tool_version,
            dependency_digest=_digest([]),
            configuration_digest=_digest({"assessment": "pqc-v0.4"}),
        ),
        replay_seed=0,
    )
    return Finding(
        id=finding_id,
        title=title,
        source="crypto-assessment",
        severity=severity,
        confidence="high",
        cwe=["CWE-327"],
        target_node_id=target_node_id,
        evidence=evidence,
        reproduction=ReproductionRecipe(
            command=command,
            working_directory=".",
            expected=title,
        ),
        remediation=remediation,
    )


def normalize_crypto_findings(
    targets: CryptoFindingTargets,
    observed_at: datetime,
    *,
    ml_kem: MLKEMMigration,
    ml_dsa: MLDSAMigration,
    agility: CryptoAgilityScore,
    downgrade: DowngradeValidation,
    tool_version: str = "0.0.0",
) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    assessment_command = ["lattence", "pqc", "assess", "."]
    if not ml_kem.compatible:
        findings.append(
            _finding(
                finding_id="LT-PQC-201",
                title="ML-KEM migration is blocked",
                severity="high",
                target_node_id=targets.ml_kem,
                summary={
                    "target": ml_kem.target,
                    "status": ml_kem.status,
                    "blocking_factors": list(ml_kem.blocking_factors),
                },
                observed_at=observed_at,
                remediation=f"Enable {ml_kem.target} and test a hybrid transition.",
                command=assessment_command,
                tool_version=tool_version,
            )
        )
    if not ml_dsa.compatible:
        findings.append(
            _finding(
                finding_id="LT-PQC-202",
                title="ML-DSA migration is blocked",
                severity="high",
                target_node_id=targets.ml_dsa,
                summary={
                    "target": ml_dsa.target,
                    "status": ml_dsa.status,
                    "blocking_factors": list(ml_dsa.blocking_factors),
                },
                observed_at=observed_at,
                remediation=f"Enable {ml_dsa.target} and test hybrid credentials.",
                command=assessment_command,
                tool_version=tool_version,
            )
        )
    if agility.percentage < 100:
        findings.append(
            _finding(
                finding_id="LT-PQC-203",
                title="Cryptographic agility is limited",
                severity="medium",
                target_node_id=targets.agility,
                summary={
                    "percentage": agility.percentage,
                    "limiting_factors": list(agility.limiting_factors),
                },
                observed_at=observed_at,
                remediation="Resolve every reported crypto agility limiting factor.",
                command=assessment_command,
                tool_version=tool_version,
            )
        )
    if downgrade.status == "vulnerable":
        findings.append(
            _finding(
                finding_id="LT-PQC-204",
                title="A cryptographic downgrade was accepted",
                severity="critical",
                target_node_id=targets.downgrade,
                summary={
                    "status": downgrade.status,
                    "outcomes": [item.outcome for item in downgrade.evidence],
                },
                observed_at=observed_at,
                remediation="Reject classical-only negotiation after PQC is enabled.",
                command=["lattence", "crypto", "chaos", "."],
                tool_version=tool_version,
            )
        )
    elif downgrade.status == "blocked":
        findings.append(
            _finding(
                finding_id="LT-PQC-205",
                title="Cryptographic downgrade validation is incomplete",
                severity="low",
                target_node_id=targets.downgrade,
                summary={
                    "status": downgrade.status,
                    "blocking_reasons": list(downgrade.blocking_reasons),
                },
                observed_at=observed_at,
                remediation=(
                    "Run both downgrade probes to completion and verify rollback."
                ),
                command=["lattence", "crypto", "chaos", "."],
                tool_version=tool_version,
            )
        )
    return tuple(sorted(findings, key=lambda finding: finding.id))
