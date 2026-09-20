import hashlib
import json
import subprocess
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
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

type PromptfooExecutor = Callable[[list[str], Path], tuple[int, str]]


def _default_executor(command: list[str], output_path: Path) -> tuple[int, str]:
    try:
        result = subprocess.run(command, capture_output=True, check=False, text=True)
    except OSError as error:
        return 127, str(error)
    if result.returncode == 0 and not output_path.is_file():
        return 3, f"Promptfoo did not write output: {output_path}"
    return result.returncode, result.stderr.strip()


def _safe_name(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value)


class PromptfooProvider:
    def __init__(
        self,
        *,
        executor: PromptfooExecutor | None = None,
        work_directory: Path | None = None,
    ) -> None:
        self._executor = executor or _default_executor
        self._work_directory = work_directory

    def discover(self, project: Project) -> list[Node]:
        return []

    def generate_tests(self, graph: SecurityGraph) -> list[TestCase]:
        tests: list[TestCase] = []
        for node in sorted(graph.nodes, key=lambda item: item.id):
            if node.type != "model":
                continue
            target = node.metadata.get(
                "promptfoo_target", node.endpoint or node.model_name
            )
            if not isinstance(target, str):
                continue
            tests.append(
                TestCase(
                    id=f"promptfoo:{node.id}",
                    title=f"Promptfoo scan of {node.name}",
                    target_node_id=node.id,
                    inputs={"target": target},
                    timeout_seconds=900,
                    replay_seed=0,
                )
            )
        return tests

    def execute(self, test: TestCase) -> RawResult:
        if self._work_directory is not None:
            return self._execute_in(test, self._work_directory)
        with tempfile.TemporaryDirectory(prefix="lattence-promptfoo-") as directory:
            return self._execute_in(test, Path(directory))

    def _execute_in(self, test: TestCase, directory: Path) -> RawResult:
        directory.mkdir(parents=True, exist_ok=True)
        output_path = directory / f"{_safe_name(test.id)}.json"
        target = test.inputs.get("target")
        if not isinstance(target, str):
            return self.raw_result(
                test, {}, error="Promptfoo target configuration is invalid"
            )
        command = [
            "promptfoo",
            "redteam",
            "run",
            "--target",
            target,
            "--output",
            str(output_path),
        ]
        started_at = datetime.now(UTC)
        return_code, error = self._executor(command, output_path)
        finished_at = datetime.now(UTC)
        result: JsonValue = {}
        if return_code == 0:
            try:
                result = cast(
                    JsonValue,
                    json.loads(output_path.read_text(encoding="utf-8")),
                )
            except (OSError, json.JSONDecodeError) as read_error:
                error = f"invalid Promptfoo JSON output: {read_error}"
        return self.raw_result(
            test,
            result,
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
            provider="promptfoo",
            test_id=test.id,
            started_at=started_at or now,
            finished_at=finished_at or now,
            payload={
                "command": command or ["promptfoo"],
                "results": results,
                "target_node_id": test.target_node_id,
            },
            error=error,
        )

    def normalize_results(self, raw: RawResult) -> list[Finding]:
        if raw.error or not isinstance(raw.payload, dict):
            return []
        target = raw.payload.get("target_node_id")
        document = raw.payload.get("results")
        command_value = raw.payload.get("command")
        if not isinstance(target, str) or not isinstance(document, dict):
            return []
        envelope = document.get("results")
        if not isinstance(envelope, dict):
            return []
        results = envelope.get("results")
        if not isinstance(results, list):
            return []
        command = (
            [item for item in command_value if isinstance(item, str)]
            if isinstance(command_value, list)
            else ["promptfoo"]
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
        if not isinstance(result, dict) or result.get("success") is not False:
            return None
        grading = result.get("gradingResult")
        reason = grading.get("reason") if isinstance(grading, dict) else None
        if not isinstance(reason, str):
            reason = "red-team assertion failed"
        digest = hashlib.sha256(f"{target}:{reason}".encode()).hexdigest()
        serialized = json.dumps(result, sort_keys=True).encode()
        return Finding(
            id=f"LT-PROMPTFOO{digest[:8].upper()}-001",
            title=f"Promptfoo {reason}",
            source="promptfoo",
            severity="info",
            confidence="low",
            target_node_id=target,
            evidence=EvidenceBundle(
                id=f"evidence:promptfoo:{digest[:16]}",
                inputs=[
                    EvidenceInput(
                        name="promptfoo-result",
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
                expected="Promptfoo reports a failed red-team assertion.",
                offline=False,
            ),
            remediation=(
                "Review the failed assertion and strengthen the target boundary."
            ),
        )
