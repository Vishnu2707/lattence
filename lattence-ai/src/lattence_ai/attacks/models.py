from datetime import datetime
from enum import StrEnum

from lattence.graph import JsonValue, NodeId, UtcDateTime
from pydantic import BaseModel, ConfigDict, Field


class AttackModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class TestCase(AttackModel):
    id: str
    title: str
    target_node_id: NodeId
    inputs: dict[str, JsonValue] = Field(default_factory=dict)
    timeout_seconds: float = Field(gt=0)
    replay_seed: int


class RawResult(AttackModel):
    provider: str
    test_id: str
    started_at: UtcDateTime
    finished_at: UtcDateTime
    payload: JsonValue
    error: str | None = None


class ObservationResult(AttackModel):
    rule_id: str
    test_id: str
    target_node_id: NodeId
    matched: bool
    facts: dict[str, JsonValue] = Field(default_factory=dict)
    observed_at: datetime


class VerificationOutcome(StrEnum):
    VULNERABLE = "vulnerable"
    RESOLVED = "resolved"
    NOT_FOUND = "not_found"
