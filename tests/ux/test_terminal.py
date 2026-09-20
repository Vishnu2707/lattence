from datetime import UTC, datetime
from pathlib import Path

from lattence.cli.presentation import (
    render_attack_summary,
    render_banner,
    render_scan_summary,
)
from lattence.evidence import Report, ReportSummary, ToolInfo
from lattence.graph import Agent, Project, SecurityGraph, Tool


def _report() -> Report:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    nodes = [Agent(id="agent:one", name="one"), Tool(id="tool:one", name="one")]
    project = Project(
        id="project:fixture",
        name="fixture",
        root=".",
        scanned_at=timestamp,
        nodes=nodes,
    )
    graph = SecurityGraph(
        project_id=project.id, nodes=nodes, edges=[], generated_at=timestamp
    )
    return Report(
        tool=ToolInfo(version="0.0.0"),
        project=project,
        graph=graph,
        findings=[],
        generated_at=timestamp,
        summary=ReportSummary(
            total=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
            pqc_readiness=0,
        ),
    )


def test_plain_scan_summary_has_required_sections_without_escapes() -> None:
    rendered = render_scan_summary(
        _report(), Path("."), Path("lattence-report.html"), 1.2
    )

    assert "LATTENCE  scan  ." in rendered
    assert "DISCOVERY" in rendered
    assert "AI ATTACK SURFACE" in rendered
    assert "CRYPTOGRAPHY" in rendered
    assert "Agents                1" in rendered
    assert "\x1b[" not in rendered


def test_color_mode_uses_terminal_styles() -> None:
    rendered = render_scan_summary(
        _report(), Path("."), Path("lattence-report.html"), 1.2, color=True
    )

    assert "\x1b[" in rendered


def test_banner_is_a_plain_block_of_no_more_than_six_lines() -> None:
    banner = render_banner()

    lines = banner.rstrip("\n").splitlines()
    assert 1 <= len(lines) <= 6
    assert "\x1b[" not in banner


def test_attack_summary_plain_mode_has_no_escapes() -> None:
    plain = "LATTENCE  attack  .\n\nVULNERABLE  LT-AI-001  Direct  agent:x\n"

    assert render_attack_summary(plain) == plain
    assert "\x1b[" not in render_attack_summary(plain)


def test_attack_summary_color_mode_styles_vulnerable_lines() -> None:
    plain = "LATTENCE  attack  .\n\nVULNERABLE  LT-AI-001  Direct  agent:x\n"

    rendered = render_attack_summary(plain, color=True)

    assert "\x1b[" in rendered
    assert "VULNERABLE  LT-AI-001  Direct  agent:x" in rendered
