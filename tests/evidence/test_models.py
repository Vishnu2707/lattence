from datetime import UTC, datetime, timedelta

import pytest
from lattence.evidence import (
    EnvironmentFingerprint,
    EvidenceBundle,
    EvidenceInput,
    Finding,
    PolicyDecision,
    ReproductionRecipe,
    TranscriptEntry,
)
from pydantic import ValidationError

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def bundle() -> EvidenceBundle:
    return EvidenceBundle(
        id="evidence:LT-AI-001",
        inputs=[
            EvidenceInput(
                name="fixture",
                media_type="text/plain",
                sha256="0" * 64,
                value="controlled input",
            )
        ],
        transcript=[
            TranscriptEntry(
                sequence=1,
                actor="target",
                kind="response",
                content={"status": "observed"},
                timestamp=NOW,
            )
        ],
        telemetry_spans=[],
        policy_decision=PolicyDecision(
            policy_id="policy:prompt-boundary",
            outcome="fail",
            reason="Untrusted instructions reached the target.",
        ),
        started_at=NOW,
        finished_at=NOW + timedelta(milliseconds=10),
        environment=EnvironmentFingerprint(
            platform="test",
            python="3.12",
            lattence_version="0.0.0",
            dependency_digest="a" * 64,
            configuration_digest="b" * 64,
        ),
        replay_seed=7,
    )


def test_finding_round_trip_preserves_evidence() -> None:
    finding = Finding(
        id="LT-AI-001",
        title="Untrusted prompt reaches tool",
        source="native",
        severity="high",
        confidence="high",
        owasp_llm=["LLM01"],
        target_node_id="agent:main",
        evidence=bundle(),
        reproduction=ReproductionRecipe(
            command=["lattence", "verify", "LT-AI-001"],
            working_directory=".",
            expected="VULNERABLE",
        ),
        remediation="Separate untrusted context from executable instructions.",
    )

    restored = Finding.model_validate_json(finding.model_dump_json())

    assert restored == finding
    assert restored.evidence.replay_seed == 7
    assert restored.status == "open"


def test_finding_rejects_invalid_identifier_and_unknown_fields() -> None:
    values = {
        "id": "bad-id",
        "title": "Bad id",
        "source": "native",
        "severity": "low",
        "confidence": "low",
        "target_node_id": "agent:main",
        "evidence": bundle(),
        "reproduction": ReproductionRecipe(
            command=["lattence", "verify", "bad-id"],
            working_directory=".",
            expected="BLOCKED",
        ),
        "remediation": "Use a valid identifier.",
        "unexpected": True,
    }

    with pytest.raises(ValidationError):
        Finding.model_validate(values)


def test_evidence_rejects_reversed_interval() -> None:
    values = bundle().model_dump()
    values["finished_at"] = NOW - timedelta(seconds=1)

    with pytest.raises(ValidationError, match="finished_at"):
        EvidenceBundle.model_validate(values)


def test_evidence_rejects_duplicate_transcript_sequence() -> None:
    values = bundle().model_dump()
    values["transcript"] = [values["transcript"][0], values["transcript"][0]]

    with pytest.raises(ValidationError, match="transcript sequence"):
        EvidenceBundle.model_validate(values)
