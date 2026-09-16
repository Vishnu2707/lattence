import json
from pathlib import Path
from typing import Any, Literal

import jsonschema
from lattence.graph import Project, SecurityGraph, UtcDateTime
from pydantic import BaseModel, ConfigDict, Field

from .models import Finding


class ReportModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ToolInfo(ReportModel):
    name: Literal["lattence"] = "lattence"
    version: str


class ReportSummary(ReportModel):
    total: int = Field(ge=0)
    critical: int = Field(ge=0)
    high: int = Field(ge=0)
    medium: int = Field(ge=0)
    low: int = Field(ge=0)
    info: int = Field(ge=0)
    pqc_readiness: float = Field(ge=0, le=100)
    quantum_vulnerable_assets: int = Field(default=0, ge=0)
    quantum_vulnerable_paths: int = Field(default=0, ge=0)


class Report(ReportModel):
    schema_version: Literal["1"] = "1"
    tool: ToolInfo
    project: Project
    graph: SecurityGraph
    findings: list[Finding]
    generated_at: UtcDateTime
    summary: ReportSummary


def build_report(
    project: Project,
    graph: SecurityGraph,
    findings: list[Finding],
    tool_version: str,
    pqc_readiness: float,
    *,
    quantum_vulnerable_assets: int = 0,
    quantum_vulnerable_paths: int = 0,
) -> Report:
    ordered = sorted(findings, key=lambda item: item.id)
    counts = {
        severity: sum(item.severity == severity for item in ordered)
        for severity in ("critical", "high", "medium", "low", "info")
    }
    return Report(
        tool=ToolInfo(version=tool_version),
        project=project,
        graph=graph,
        findings=ordered,
        generated_at=graph.generated_at,
        summary=ReportSummary(
            total=len(ordered),
            critical=counts["critical"],
            high=counts["high"],
            medium=counts["medium"],
            low=counts["low"],
            info=counts["info"],
            pqc_readiness=pqc_readiness,
            quantum_vulnerable_assets=quantum_vulnerable_assets,
            quantum_vulnerable_paths=quantum_vulnerable_paths,
        ),
    )


def _ordered(value: Any, field: str | None = None) -> Any:
    if isinstance(value, dict):
        return {key: _ordered(item, key) for key, item in value.items()}
    if isinstance(value, list):
        items = [_ordered(item) for item in value]
        if field in {
            "capabilities",
            "cwe",
            "data_classes",
            "owasp_agentic",
            "owasp_llm",
            "permissions",
            "scopes",
            "tags",
        }:
            return sorted(items)
        if field in {"edges", "findings", "nodes"}:
            return sorted(items, key=lambda item: item["id"])
        return items
    return value


def report_json(report: Report, schema_path: Path | None = None) -> str:
    document = _ordered(report.model_dump(mode="json"))
    if schema_path is not None:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema, format_checker=None).validate(document)
    return json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_json_report(
    report: Report, destination: Path, schema_path: Path | None = None
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(report_json(report, schema_path), encoding="utf-8")
