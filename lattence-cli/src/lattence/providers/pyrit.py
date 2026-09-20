import hashlib
import json
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

from lattence.evidence import (
    EnvironmentFingerprint,
    EvidenceBundle,
    EvidenceInput,
    Finding,
    PolicyDecision,
    ReproductionRecipe,
)
from lattence.graph import JsonValue, Node, Project, SecurityGraph
from lattence_ai import RawResult, TestCase

type PyritExecutor = Callable[[list[str]], tuple[int, str, str]]


def _default_executor(command: list[str]) -> tuple[int, str, str]:
    try:
        result = subprocess.run(command, capture_output=True, check=False, text=True)
    except OSError as error:
        return 127, "", str(error)
    return result.returncode, result.stdout, result.stderr.strip()


class PyritProvider:
    def __init__(self, *, executor: PyritExecutor | None = None) -> None:
        self._executor = executor or _default_executor

    def discover(self, project: Project) -> list[Node]:
        return []

    def generate_tests(self, graph: SecurityGraph) -> list[TestCase]:
        tests: list[TestCase] = []
        for node in sorted(graph.nodes, key=lambda item: item.id):
            if node.type != "model":
                continue
            scenario = node.metadata.get("pyrit_scenario", "benchmark.adversarial")
            target = node.metadata.get("pyrit_target", node.name)
            if not isinstance(scenario, str) or not isinstance(target, str):
                continue
            tests.append(
                TestCase(
                    id=f"pyrit:{node.id}",
                    title=f"PyRIT scan of {node.name}",
                    target_node_id=node.id,
                    inputs={"scenario": scenario, "target": target},
                    timeout_seconds=900,
                    replay_seed=0,
                )
            )
        return tests

    def execute(self, test: TestCase) -> RawResult:
        scenario = test.inputs.get("scenario")
        target = test.inputs.get("target")
        if not isinstance(scenario, str) or not isinstance(target, str):
            return self.raw_result(
                test, {}, error="PyRIT target configuration is invalid"
            )
        command = [
            "pyrit_scan",
            "run",
            scenario,
            "--target",
            target,
            "--output-format",
            "json",
        ]
        started_at = datetime.now(UTC)
        return_code, output, error = self._executor(command)
        finished_at = datetime.now(UTC)
        payload: JsonValue = {}
        if return_code == 0:
            try:
                payload = cast(JsonValue, json.loads(output))
            except json.JSONDecodeError as parse_error:
                error = f"invalid PyRIT JSON output: {parse_error}"
        return self.raw_result(
            test,
            payload,
            command=command,
            error=error or None,
            started_at=started_at,
            finished_at=finished_at,
        )

    def raw_result(
        self,
        test: TestCase,
        results: JsonValue,
        *,
        command: list[str] | None = None,
        error: str | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> RawResult:
        now = datetime.now(UTC)
        return RawResult(
            provider="pyrit",
            test_id=test.id,
            started_at=started_at or now,
            finished_at=finished_at or now,
            payload={
                "command": command or ["pyrit_scan"],
                "results": results,
                "target_node_id": test.target_node_id,
            },
            error=error,
        )

    def normalize_results(self, raw: RawResult) -> list[Finding]:
        if raw.error or not isinstance(raw.payload, dict):
            return []
        target = raw.payload.get("target_node_id")
        result_document = raw.payload.get("results")
        command_value = raw.payload.get("command")
        if not isinstance(target, str) or not isinstance(result_document, dict):
            return []
        results = result_document.get("results")
        if not isinstance(results, list):
            return []
        command = (
            [item for item in command_value if isinstance(item, str)]
            if isinstance(command_value, list)
            else ["pyrit_scan"]
        )
        findings: list[Finding] = []
        for result in results:
            finding = self._normalize_result(raw, target, command, result)
            if finding is not None:
                findings.append(finding)
        return findings

    def _normalize_result(
        self,
        raw: RawResult,
        target: str,
        command: list[str],
        result: JsonValue,
    ) -> Finding | None:
        if not isinstance(result, dict):
            return None
        outcome = result.get("outcome")
        attack_success = result.get("attack_success")
        if not (
            attack_success is True
            or isinstance(outcome, str)
            and outcome.lower() in {"success", "succeeded"}
        ):
            return None
        objective = result.get("objective", "successful attack")
        if not isinstance(objective, str):
            objective = "successful attack"
        digest = hashlib.sha256(f"{target}:{objective}".encode()).hexdigest()
        serialized = json.dumps(result, sort_keys=True).encode()
        return Finding(
            id=f"LT-PYRIT{digest[:8].upper()}-001",
            title=f"PyRIT {objective}",
            source="pyrit",
            severity="info",
            confidence="low",
            target_node_id=target,
            evidence=EvidenceBundle(
                id=f"evidence:pyrit:{digest[:16]}",
                inputs=[
                    EvidenceInput(
                        name="pyrit-result",
                        media_type="application/json",
                        sha256=hashlib.sha256(serialized).hexdigest(),
                        value=result,
                    )
                ],
                transcript=[],
                telemetry_spans=[],
                policy_decision=PolicyDecision(
                    policy_id="policy:provider-normalization",
                    outcome="skip",
                    reason="Central policy evaluation has not run.",
                ),
                started_at=raw.started_at,
                finished_at=raw.finished_at,
                environment=EnvironmentFingerprint(
                    platform="external",
                    python="unknown",
                    lattence_version="0.0.0",
                    dependency_digest="0" * 64,
                    configuration_digest=hashlib.sha256(
                        json.dumps(command).encode()
                    ).hexdigest(),
                ),
                replay_seed=0,
            ),
            reproduction=ReproductionRecipe(
                command=command,
                working_directory=".",
                expected="PyRIT reports a successful attack.",
                offline=False,
            ),
            remediation=(
                "Review the successful objective and strengthen the target boundary."
            ),
        )
