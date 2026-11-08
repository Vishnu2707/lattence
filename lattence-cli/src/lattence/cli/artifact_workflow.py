import json
from dataclasses import dataclass
from pathlib import Path

from lattence.evidence import (
    Report,
    SecurityPresentation,
    report_json,
    sarif_json,
    write_html_report,
    write_json_report,
)
from lattence.graph import security_graph_json
from pydantic import ValidationError


@dataclass(frozen=True)
class ArtifactPaths:
    json: Path
    html: Path


def schema_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "docs" / "schemas" / "report.v1.json"
        if candidate.is_file():
            return candidate
    installed = Path(__file__).resolve().parents[1] / "schemas" / "report.v1.json"
    if installed.is_file():
        return installed
    raise RuntimeError("cannot locate bundled report schema")


def artifact_paths(output: Path) -> ArtifactPaths:
    if output.suffix.lower() in {".html", ".json"}:
        base = output.with_suffix("")
        return ArtifactPaths(base.with_suffix(".json"), base.with_suffix(".html"))
    return ArtifactPaths(
        output / "lattence-report.json", output / "lattence-report.html"
    )


def _sibling_presentation(output: Path) -> SecurityPresentation | None:
    directory = output.parent if output.suffix else output
    candidate = directory / "presentation.json"
    if not candidate.is_file():
        return None
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        payload.pop("cross_layer_summary", None)
        return SecurityPresentation.model_validate(payload)
    except (ValidationError, ValueError):
        return None


def write_report_artifacts(report: Report, output: Path) -> ArtifactPaths:
    paths = artifact_paths(output)
    write_json_report(report, paths.json, schema_path())
    write_html_report(report, paths.html, _sibling_presentation(output))
    return paths


def load_report(input_path: Path) -> Report:
    source = input_path / "lattence-report.json" if input_path.is_dir() else input_path
    return Report.model_validate_json(source.read_text(encoding="utf-8"))


def write_graph(report: Report, output: Path) -> Path:
    destination = output / "lattence-graph.json" if output.is_dir() else output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(security_graph_json(report.graph), encoding="utf-8")
    return destination


def write_sarif(report: Report, output: Path) -> Path:
    destination = output / "lattence.sarif.json" if output.is_dir() else output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(sarif_json(report), encoding="utf-8")
    return destination


def machine_report(report: Report) -> str:
    return report_json(report, schema_path())
