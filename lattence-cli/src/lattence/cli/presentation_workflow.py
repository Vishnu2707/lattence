from pathlib import Path

from lattence.evidence import (
    SecurityPresentation,
    build_cross_layer_chain,
    build_security_presentation,
    presentation_json,
)
from lattence_ai.attacks import correlate_cross_layer_findings

from .crypto_workflow import create_crypto_assessment
from .workflow import create_report


def create_security_presentation(
    root: Path, output: Path | None = None
) -> SecurityPresentation:
    report = create_report(root, output)
    assessment = create_crypto_assessment(root, output=output, base_report=report)
    findings = tuple(
        sorted(
            (*report.findings, *assessment.report.findings),
            key=lambda finding: finding.id,
        )
    )
    correlations = correlate_cross_layer_findings(report.graph, findings, max_depth=4)
    chains = [
        build_cross_layer_chain(
            item.source_finding_id,
            item.crypto_finding_id,
            item.path,
            item.explanation,
            item.evidence_refs,
        )
        for item in correlations
    ]
    return build_security_presentation(
        report.project,
        report.graph,
        findings,
        chains,
    )


def write_dashboard_data(presentation: SecurityPresentation, output: Path) -> Path:
    destination = output if output.suffix == ".json" else output / "presentation.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(presentation_json(presentation), encoding="utf-8")
    return destination
