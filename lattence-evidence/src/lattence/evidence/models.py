from typing import Annotated, Literal, Self

from lattence.graph import JsonValue, NodeId, UtcDateTime
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

type Digest = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
type FindingId = Annotated[
    str, StringConstraints(pattern=r"^LT-[A-Z][A-Z0-9]*-[0-9]{3}$")
]
type Severity = Literal["critical", "high", "medium", "low", "info"]
type Confidence = Literal["high", "medium", "low"]
type FindingStatus = Literal["open", "accepted", "fixed", "false_positive"]
type PolicyOutcome = Literal["pass", "fail", "warn", "skip", "blocked"]


class EvidenceModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EvidenceInput(EvidenceModel):
    name: str
    media_type: str
    sha256: Digest
    value: JsonValue | None = None


class TranscriptEntry(EvidenceModel):
    sequence: int = Field(ge=0)
    actor: str
    kind: str
    content: JsonValue
    timestamp: UtcDateTime


class TelemetrySpan(EvidenceModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    name: str
    start_time: UtcDateTime
    end_time: UtcDateTime
    attributes: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def interval_is_ordered(self) -> Self:
        if self.end_time < self.start_time:
            raise ValueError("end_time must not precede start_time")
        return self


class PolicyDecision(EvidenceModel):
    policy_id: str
    outcome: PolicyOutcome
    reason: str
    facts: dict[str, JsonValue] = Field(default_factory=dict)


class EnvironmentFingerprint(EvidenceModel):
    platform: str
    python: str
    lattence_version: str
    project_revision: str | None = None
    dependency_digest: Digest
    configuration_digest: Digest


class ReproductionRecipe(EvidenceModel):
    command: list[str] = Field(min_length=1)
    working_directory: str
    environment_names: list[str] = Field(default_factory=list)
    expected: str
    offline: bool = True


class EvidenceBundle(EvidenceModel):
    id: str
    inputs: list[EvidenceInput]
    transcript: list[TranscriptEntry]
    telemetry_spans: list[TelemetrySpan]
    policy_decision: PolicyDecision
    started_at: UtcDateTime
    finished_at: UtcDateTime
    environment: EnvironmentFingerprint
    replay_seed: int

    @model_validator(mode="after")
    def sequence_and_interval_are_valid(self) -> Self:
        if self.finished_at < self.started_at:
            raise ValueError("finished_at must not precede started_at")
        sequences = [entry.sequence for entry in self.transcript]
        if len(sequences) != len(set(sequences)):
            raise ValueError("transcript sequence values must be unique")
        if sequences != sorted(sequences):
            raise ValueError("transcript sequence values must be ordered")
        return self


class Finding(EvidenceModel):
    id: FindingId
    title: str
    source: str
    severity: Severity
    confidence: Confidence
    owasp_llm: list[str] = Field(default_factory=list)
    owasp_agentic: list[str] = Field(default_factory=list)
    cwe: list[str] = Field(default_factory=list)
    target_node_id: NodeId
    evidence: EvidenceBundle
    reproduction: ReproductionRecipe
    remediation: str
    status: FindingStatus = "open"
