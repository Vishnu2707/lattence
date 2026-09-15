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

type GarakExecutor = Callable[[list[str], Path], tuple[int, str]]


def _default_executor(command: list[str], report_path: Path) -> tuple[int, str]:
    try:
        result = subprocess.run(command, capture_output=True, check=False, text=True)
    except OSError as error:
        return 127, str(error)
    if result.returncode == 0 and not report_path.is_file():
        return 3, f"garak did not write report: {report_path}"
    return result.returncode, result.stderr.strip()


def _safe_name(value: str) -> str:
    return "".join(character if character.isalnum() else "-" for character in value)


class GarakProvider:
    def __init__(
        self,
        *,
        executor: GarakExecutor | None = None,
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
            tests.append(
                TestCase(
                    id=f"garak:{node.id}",
                    title=f"Garak scan of {node.name}",
                    target_node_id=node.id,
                    inputs={
                        "target_type": "rest" if node.endpoint else node.provider,
                        "target_name": node.endpoint or node.model_name,
                    },
                    timeout_seconds=900,
                    replay_seed=0,
                )
            )
        return tests

    def execute(self, test: TestCase) -> RawResult:
        if self._work_directory is not None:
            return self._execute_in(test, self._work_directory)
        with tempfile.TemporaryDirectory(prefix="lattence-garak-") as directory:
            return self._execute_in(test, Path(directory))

    def _execute_in(self, test: TestCase, directory: Path) -> RawResult:
        directory.mkdir(parents=True, exist_ok=True)
        prefix = directory / _safe_name(test.id)
        report_path = prefix.with_suffix(".report.jsonl")
        target_type = test.inputs.get("target_type")
        target_name = test.inputs.get("target_name")
        if not isinstance(target_type, str) or not isinstance(target_name, str):
            return self.raw_result(
                test, [], error="garak target configuration is invalid"
            )
        command = [
            "garak",
            "--target_type",
            target_type,
            "--target_name",
            target_name,
            "--report_prefix",
            str(prefix),
            "--narrow_output",
        ]
        started_at = datetime.now(UTC)
        return_code, error = self._executor(command, report_path)
        finished_at = datetime.now(UTC)
        records: list[JsonValue] = []
        if return_code == 0:
            try:
                records = [
                    cast(JsonValue, json.loads(line))
                    for line in report_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
            except (OSError, json.JSONDecodeError) as read_error:
                error = f"invalid garak report: {read_error}"
        return self.raw_result(
            test,
            records,
            command=command,
            error=error or None,
            started_at=started_at,
            finished_at=finished_at,
        )

    def raw_result(
        self,
        test: TestCase,
        records: list[JsonValue],
        *,
        command: list[str] | None = None,
        error: str | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> RawResult:
        now = datetime.now(UTC)
        return RawResult(
            provider="garak",
            test_id=test.id,
            started_at=started_at or now,
            finished_at=finished_at or now,
            payload={
                "command": command or ["garak"],
                "records": records,
                "target_node_id": test.target_node_id,
            },
            error=error,
        )

    def normalize_results(self, raw: RawResult) -> list[Finding]:
        if raw.error or not isinstance(raw.payload, dict):
            return []
        target = raw.payload.get("target_node_id")
        records = raw.payload.get("records")
        command = raw.payload.get("command")
        if not isinstance(target, str) or not isinstance(records, list):
            return []
        replay = (
            [item for item in command if isinstance(item, str)]
            if isinstance(command, list)
            else ["garak"]
        )
        findings: list[Finding] = []
        for record in records:
            finding = self._normalize_record(raw, target, replay, record)
            if finding is not None:
                findings.append(finding)
        return findings

    def _normalize_record(
        self,
        raw: RawResult,
        target: str,
        command: list[str],
        record: JsonValue,
    ) -> Finding | None:
        if not isinstance(record, dict) or record.get("entry_type") != "eval":
            return None
        passed = record.get("passed")
        total = record.get("total", record.get("total_evaluated"))
        if not isinstance(passed, int) or not isinstance(total, int) or passed >= total:
            return None
        probe = record.get("probe")
        detector = record.get("detector")
        if not isinstance(probe, str) or not isinstance(detector, str):
            return None
        failed = total - passed
        digest = hashlib.sha256(f"{target}:{probe}:{detector}".encode()).hexdigest()
        evidence_value: dict[str, JsonValue] = {
            "detector": detector,
            "failed": failed,
            "passed": passed,
            "probe": probe,
            "total": total,
        }
        serialized = json.dumps(evidence_value, sort_keys=True).encode()
        return Finding(
            id=f"LT-GARAK{digest[:8].upper()}-001",
            title=f"Garak {probe}",
            source="garak",
            severity="info",
            confidence="low",
            target_node_id=target,
            evidence=EvidenceBundle(
                id=f"evidence:garak:{digest[:16]}",
                inputs=[
                    EvidenceInput(
                        name="garak-evaluation",
                        media_type="application/json",
                        sha256=hashlib.sha256(serialized).hexdigest(),
                        value=evidence_value,
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
                expected="Garak reports one or more failed evaluations.",
                offline=False,
            ),
            remediation=(
                f"Review and mitigate the {probe} behavior detected by {detector}."
            ),
        )
