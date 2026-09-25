from typing import Literal, Self

from lattence.graph import JsonValue
from pydantic import BaseModel, ConfigDict, Field, model_validator


class RuleModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RequiresPathSpec(RuleModel):
    """Requires a real graph path from a source node type to the matched node.

    A rule with this predicate does not fire on node shape alone: it also
    requires the existing security graph traversal to find at least one path
    of `edge_types` from some node of `from_type` to the node under test,
    within `max_depth` hops. This is how a rule expresses "untrusted data
    genuinely reaches this sink" instead of "a node exists that looks like
    a sink."
    """

    from_type: str
    edge_types: list[str] = Field(min_length=1)
    max_depth: int = Field(default=6, ge=1)


class MatchSpec(RuleModel):
    paths: list[str] | None = None
    dependencies: list[str] | None = None
    syntax: list[str] | None = None
    config: dict[str, JsonValue] | None = None
    graph: dict[str, JsonValue] | None = None
    requires_path: RequiresPathSpec | None = None

    @model_validator(mode="after")
    def contains_predicate(self) -> Self:
        if not any(
            value is not None
            for value in (
                self.paths,
                self.dependencies,
                self.syntax,
                self.config,
                self.graph,
            )
        ):
            raise ValueError("match must contain at least one predicate")
        return self


class FindingTemplate(RuleModel):
    message: str = Field(min_length=1)
    remediation: str = Field(min_length=1)
    owasp_llm: list[str] = Field(default_factory=list)
    owasp_agentic: list[str] = Field(default_factory=list)
    cwe: list[str] = Field(default_factory=list)


class RuleTest(RuleModel):
    name: str
    fixture: str
    expect_match: bool


class RulePack(RuleModel):
    version: Literal["1"]
    id: str
    kind: Literal["detection", "attack", "policy"]
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    severity: Literal["critical", "high", "medium", "low", "info"]
    confidence: Literal["high", "medium", "low"]
    applies_to: list[str] = Field(min_length=1)
    match: MatchSpec
    finding: FindingTemplate
    tests: list[RuleTest] = Field(default_factory=list)
