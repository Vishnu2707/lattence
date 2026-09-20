import json
from pathlib import Path
from typing import Any

import jsonschema
from lattence.graph import JsonValue, Node

from .reporting import Report

_SARIF_SCHEMA_URI = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/"
    "master/Schemata/sarif-schema-2.1.0.json"
)
_LEVEL_BY_SEVERITY = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
    "info": "note",
}


def _location(node: Node | None) -> dict[str, JsonValue] | None:
    if node is None or node.source is None:
        return None
    region: dict[str, JsonValue] = {}
    if node.source.line is not None:
        region["startLine"] = node.source.line
    if node.source.column is not None:
        region["startColumn"] = node.source.column
    physical: dict[str, JsonValue] = {"artifactLocation": {"uri": node.source.path}}
    if region:
        physical["region"] = region
    return {"physicalLocation": physical}


def build_sarif(report: Report) -> dict[str, JsonValue]:
    nodes_by_id = {node.id: node for node in report.graph.nodes}
    rules: dict[str, dict[str, JsonValue]] = {}
    results: list[JsonValue] = []
    for finding in sorted(report.findings, key=lambda item: item.id):
        rules.setdefault(
            finding.id,
            {
                "id": finding.id,
                "name": finding.title,
                "shortDescription": {"text": finding.title},
                "fullDescription": {"text": finding.remediation},
                "properties": {
                    "owaspLlm": list(finding.owasp_llm),
                    "owaspAgentic": list(finding.owasp_agentic),
                    "cwe": list(finding.cwe),
                },
            },
        )
        result: dict[str, JsonValue] = {
            "ruleId": finding.id,
            "level": _LEVEL_BY_SEVERITY[finding.severity],
            "message": {"text": f"{finding.title} ({finding.target_node_id})"},
        }
        location = _location(nodes_by_id.get(finding.target_node_id))
        if location is not None:
            result["locations"] = [location]
        results.append(result)
    return {
        "$schema": _SARIF_SCHEMA_URI,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": report.tool.name,
                        "version": report.tool.version,
                        "informationUri": "https://github.com/Vishnu2707/lattence",
                        "rules": [rules[key] for key in sorted(rules)],
                    }
                },
                "results": results,
            }
        ],
    }


def _sarif_schema_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "docs" / "schemas" / "sarif-2.1.0.json"
        if candidate.is_file():
            return candidate
    installed = Path(__file__).resolve().parents[1] / "schemas" / "sarif-2.1.0.json"
    if installed.is_file():
        return installed
    raise RuntimeError("cannot locate bundled SARIF schema")


def sarif_json(report: Report, schema_path: Path | None = None) -> str:
    document: dict[str, Any] = build_sarif(report)
    schema = json.loads(
        (schema_path or _sarif_schema_path()).read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator(schema, format_checker=None).validate(document)
    return json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
