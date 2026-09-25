import hashlib
from collections.abc import Iterable
from typing import cast

from lattence.discovery import RulePack
from lattence.discovery.models import RequiresPathSpec
from lattence.evidence import Report
from lattence.graph import EdgeType, JsonValue, Node, SecurityGraph, find_attack_paths

from .models import ObservationResult, RawResult, TestCase, VerificationOutcome


def _seed(rule_id: str, target_id: str) -> int:
    digest = hashlib.sha256(f"{rule_id}:{target_id}".encode()).digest()
    return int.from_bytes(digest[:8])


def _read_field(node: Node, name: str) -> JsonValue:
    value: JsonValue = node.model_dump(mode="json")
    for part in name.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def _predicate(node: Node, predicate: dict[str, JsonValue] | None) -> bool:
    if not predicate:
        return True
    field = predicate.get("field")
    if not isinstance(field, str):
        return False
    value = _read_field(node, field)
    if "exists" in predicate:
        return (value is not None) is bool(predicate["exists"])
    if "equals" in predicate:
        return value == predicate["equals"]
    if "contains" in predicate:
        expected = predicate["contains"]
        if isinstance(value, str) and isinstance(expected, str):
            return expected.lower() in value.lower()
        if isinstance(value, list):
            return expected in value
    return False


def _has_real_path(
    graph: SecurityGraph, target_id: str, spec: RequiresPathSpec
) -> bool:
    """True only if a genuine graph path reaches the target from spec.from_type.

    This is the taint check: a node shaped like a sink is not enough, the
    existing security graph traversal must find a real edge path from at
    least one node of `spec.from_type` to the target node. Uses the shared
    `find_attack_paths` traversal in `lattence.graph`, not a second
    mechanism.
    """
    source_ids = [node.id for node in graph.nodes if node.type == spec.from_type]
    if not source_ids:
        return False
    edge_types = cast(frozenset[EdgeType], frozenset(spec.edge_types))
    paths = find_attack_paths(
        graph,
        source_ids,
        [target_id],
        max_depth=spec.max_depth,
        edge_types=edge_types,
    )
    return len(paths) > 0


class AttackRunner:
    def __init__(self, graph: SecurityGraph, rules: Iterable[RulePack]) -> None:
        self.graph = graph
        self.rules = tuple(
            sorted(
                (rule for rule in rules if rule.kind == "attack"),
                key=lambda item: item.id,
            )
        )
        self._rules = {rule.id: rule for rule in self.rules}
        self._nodes = {node.id: node for node in graph.nodes}

    def generate_tests(self) -> tuple[TestCase, ...]:
        tests: list[TestCase] = []
        for rule in self.rules:
            for node in sorted(self.graph.nodes, key=lambda item: item.id):
                if node.type not in rule.applies_to:
                    continue
                tests.append(
                    TestCase(
                        id=f"{rule.id}:{node.id}",
                        title=rule.title,
                        target_node_id=node.id,
                        inputs={"rule_id": rule.id},
                        timeout_seconds=30.0,
                        replay_seed=_seed(rule.id, node.id),
                    )
                )
        return tuple(tests)

    def observe(self, test: TestCase) -> ObservationResult:
        rule_id = test.inputs.get("rule_id")
        if not isinstance(rule_id, str) or rule_id not in self._rules:
            raise ValueError(f"unknown attack rule for test: {test.id}")
        node = self._nodes.get(test.target_node_id)
        if node is None:
            raise ValueError(f"unknown attack target: {test.target_node_id}")
        rule = self._rules[rule_id]
        matched = _predicate(node, rule.match.graph)
        if matched and rule.match.requires_path is not None:
            matched = _has_real_path(self.graph, node.id, rule.match.requires_path)
        return ObservationResult(
            rule_id=rule.id,
            test_id=test.id,
            target_node_id=node.id,
            matched=matched,
            facts={"node_type": node.type},
            observed_at=self.graph.generated_at,
        )

    def execute(self, test: TestCase) -> RawResult:
        observation = self.observe(test)
        return RawResult(
            provider="native-rules",
            test_id=test.id,
            started_at=observation.observed_at,
            finished_at=observation.observed_at,
            payload=observation.model_dump(mode="json"),
        )

    def run(self) -> tuple[ObservationResult, ...]:
        return tuple(self.observe(test) for test in self.generate_tests())

    def replay(self, rule_id: str, target_node_id: str) -> ObservationResult | None:
        rule = self._rules.get(rule_id)
        node = self._nodes.get(target_node_id)
        if rule is None or node is None:
            return None
        test = TestCase(
            id=f"{rule_id}:{target_node_id}",
            title=rule.title,
            target_node_id=target_node_id,
            inputs={"rule_id": rule_id},
            timeout_seconds=30.0,
            replay_seed=_seed(rule_id, target_node_id),
        )
        return self.observe(test)


def verify_finding(
    report: Report, finding_id: str, rules: Iterable[RulePack]
) -> VerificationOutcome:
    finding = next((item for item in report.findings if item.id == finding_id), None)
    if finding is None:
        return VerificationOutcome.NOT_FOUND
    runner = AttackRunner(report.graph, rules)
    observation = runner.replay(finding_id, finding.target_node_id)
    if observation is None:
        return VerificationOutcome.NOT_FOUND
    if observation.matched:
        return VerificationOutcome.VULNERABLE
    return VerificationOutcome.RESOLVED
