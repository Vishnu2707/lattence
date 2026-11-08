"""Stable workflow facade over focused report, artifact, and result modules."""

from pathlib import Path

from .artifact_workflow import ArtifactPaths as ArtifactPaths
from .artifact_workflow import artifact_paths as artifact_paths
from .artifact_workflow import load_report as load_report
from .artifact_workflow import machine_report as machine_report
from .artifact_workflow import write_graph as write_graph
from .artifact_workflow import write_report_artifacts as write_report_artifacts
from .artifact_workflow import write_sarif as write_sarif
from .report_workflow import create_attack_report as create_attack_report
from .report_workflow import create_report as create_report
from .report_workflow import crypto_output_exclusions, data_root
from .report_workflow import run_external_providers as run_external_providers
from .result_workflow import VerificationResult as VerificationResult
from .result_workflow import attack_text as attack_text
from .result_workflow import exceeds_gate as exceeds_gate
from .result_workflow import readiness_json as readiness_json
from .result_workflow import record_cli_audit_event as record_cli_audit_event
from .result_workflow import severity_meets_gate as severity_meets_gate
from .result_workflow import verify_json as verify_json
from .result_workflow import verify_report as verify_report
from .result_workflow import verify_text as verify_text


def _crypto_output_exclusions(root: Path, output: Path | None) -> tuple[str, ...]:
    return crypto_output_exclusions(root, output)


def _data_root() -> Path:
    return data_root()
