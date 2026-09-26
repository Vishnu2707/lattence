from datetime import UTC, datetime
from pathlib import Path

from lattence.discovery import FindingTemplate, MatchSpec, RulePack
from lattence.evidence import (
    Report,
    build_cross_layer_chain,
    build_report,
    build_security_presentation,
    normalize_rule_finding,
    render_html_report,
    report_json,
    write_html_report,
    write_json_report,
)
from lattence.graph import (
    Agent,
    CryptoAlgorithm,
    Edge,
    Project,
    SecurityGraph,
    TopologyHop,
    TopologyPath,
)

SCHEMA = Path(__file__).parents[2] / "docs" / "schemas" / "report.v1.json"


def _report(*, assets: int = 0, paths: int = 0) -> Report:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    agent = Agent(id="agent:one", name="one")
    project = Project(
        id="project:fixture",
        name="fixture",
        root=".",
        scanned_at=timestamp,
        nodes=[agent],
    )
    graph = SecurityGraph(
        project_id=project.id,
        nodes=[agent],
        edges=[],
        generated_at=timestamp,
    )
    rule = RulePack(
        version="1",
        id="LT-AI-001",
        kind="attack",
        title="Fixture finding",
        description="Fixture rule.",
        severity="high",
        confidence="high",
        applies_to=["agent"],
        match=MatchSpec(graph={"field": "name", "equals": "one"}),
        finding=FindingTemplate(
            message="Fixture matched.", remediation="Fix the fixture."
        ),
    )
    finding = normalize_rule_finding(rule, agent.id, timestamp, 42)
    return build_report(
        project,
        graph,
        [finding],
        "0.0.0",
        25,
        quantum_vulnerable_assets=assets,
        quantum_vulnerable_paths=paths,
    )


def test_report_json_validates_and_is_stable() -> None:
    report = _report()

    rendered = report_json(report, SCHEMA)

    assert rendered == report_json(report, SCHEMA)
    assert Report.model_validate_json(rendered) == report
    assert report.summary.total == 1
    assert report.summary.high == 1


def test_report_v1_defaults_new_crypto_exposure_counts_for_old_documents() -> None:
    document = _report().model_dump(mode="json")
    del document["summary"]["quantum_vulnerable_assets"]
    del document["summary"]["quantum_vulnerable_paths"]

    restored = Report.model_validate(document)

    assert restored.summary.quantum_vulnerable_assets == 0
    assert restored.summary.quantum_vulnerable_paths == 0


def test_writes_valid_json_report(tmp_path: Path) -> None:
    destination = tmp_path / "reports" / "report.json"

    write_json_report(_report(), destination, SCHEMA)

    assert destination.read_text(encoding="utf-8").endswith("\n")


def _presentation_with_chain():
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    agent = Agent(id="agent:one", name="one")
    algorithm = CryptoAlgorithm(
        id="crypto:rsa",
        name="rsa",
        algorithm="RSA-2048",
        purpose="key_exchange",
        quantum_status="vulnerable",
    )
    edge = Edge(
        id="edge:1", source_id=agent.id, target_id=algorithm.id, type="key_exchange"
    )
    project = Project(
        id="project:fixture",
        name="fixture",
        root=".",
        scanned_at=timestamp,
        nodes=[agent, algorithm],
    )
    graph = SecurityGraph(
        project_id=project.id,
        nodes=[agent, algorithm],
        edges=[edge],
        generated_at=timestamp,
    )
    ai_rule = RulePack(
        version="1",
        id="LT-AI-001",
        kind="attack",
        title="Fixture finding",
        description="Fixture rule.",
        severity="high",
        confidence="high",
        applies_to=["agent"],
        match=MatchSpec(graph={"field": "name", "equals": "one"}),
        finding=FindingTemplate(
            message="Fixture matched.", remediation="Fix the fixture."
        ),
    )
    pqc_rule = ai_rule.model_copy(
        update={"id": "LT-PQC-203", "title": "Vulnerable algorithm"}
    )
    ai_finding = normalize_rule_finding(ai_rule, agent.id, timestamp, 1)
    pqc_finding = normalize_rule_finding(pqc_rule, algorithm.id, timestamp, 2)
    path = TopologyPath(
        node_ids=(agent.id, algorithm.id),
        hops=(
            TopologyHop(
                edge_id=edge.id,
                source_id=edge.source_id,
                target_id=edge.target_id,
                edge_type=edge.type,
                traversal="forward",
                from_node_id=agent.id,
                to_node_id=algorithm.id,
                evidence_refs=("app.py",),
            ),
        ),
    )
    chain = build_cross_layer_chain(
        ai_finding.id,
        pqc_finding.id,
        path,
        "reaches a vulnerable algorithm",
        ("app.py",),
    )
    return build_security_presentation(
        project, graph, [ai_finding, pqc_finding], [chain]
    )


def test_html_report_renders_real_cross_layer_chain_data() -> None:
    report = _report()
    presentation = _presentation_with_chain()

    rendered = render_html_report(report, presentation)

    assert "1 finding correlations across 1 distinct structural paths" in rendered
    assert "LT-AI-001 -&gt; LT-PQC-203" in rendered
    assert "key_exchange" in rendered
    assert '"cross_layer_chains"' in rendered
    assert "https://" not in rendered
    assert "http://" not in rendered
    assert "fetch(" not in rendered


def test_html_report_without_presentation_shows_empty_chain_state() -> None:
    rendered = render_html_report(_report())

    assert "No cross-layer chain data." in rendered
    assert "lattence-presentation" not in rendered


def test_html_report_sortable_severity_header_has_no_network_dependency() -> None:
    rendered = render_html_report(_report())

    assert "data-sortable" in rendered
    assert "<link " not in rendered
    assert "cdn." not in rendered


def test_html_report_is_self_contained_and_escapes_content(tmp_path: Path) -> None:
    report = _report(assets=3, paths=2).model_copy(
        update={"project": _report().project.model_copy(update={"name": "<script>"})}
    )
    destination = tmp_path / "report.html"

    write_html_report(report, destination)
    rendered = render_html_report(report)

    assert rendered.startswith("<!doctype html>")
    assert "<title><script>" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "https://" not in rendered
    assert "<b>3</b>Isolated vulnerable assets" in rendered
    assert "<b>2</b>Traversable vulnerable paths" in rendered
    assert destination.read_text(encoding="utf-8") == rendered


def test_html_report_truncates_findings_and_nodes_past_the_table_cap() -> None:
    """Regression guard: a broken run once produced a 2,312-node graph and a
    14MB HTML dashboard, largely because the whole raw report was embedded
    twice (once per table row, once again as a full inline JSON dump). This
    pins the fix: tables cap at 200 rows, most severe first, with a note
    pointing at the full JSON file, and the raw JSON dump is skipped above
    500,000 bytes in favor of the same pointer."""
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    agent = Agent(id="agent:one", name="one")
    project = Project(
        id="project:fixture",
        name="fixture",
        root=".",
        scanned_at=timestamp,
        nodes=[agent],
    )
    many_nodes = [Agent(id=f"agent:extra:{i}", name=f"extra-{i}") for i in range(250)]
    graph = SecurityGraph(
        project_id=project.id,
        nodes=[agent, *many_nodes],
        edges=[],
        generated_at=timestamp,
    )
    rule = RulePack(
        version="1",
        id="LT-AI-001",
        kind="attack",
        title="Fixture finding",
        description="Fixture rule.",
        severity="high",
        confidence="high",
        applies_to=["agent"],
        match=MatchSpec(graph={"field": "name", "equals": "one"}),
        finding=FindingTemplate(
            message="Fixture matched.", remediation="Fix the fixture."
        ),
    )
    findings = [
        normalize_rule_finding(rule, agent.id, timestamp, seed).model_copy(
            update={"id": f"LT-AI-001-{seed}"}
        )
        for seed in range(250)
    ]
    report = build_report(project, graph, findings, "0.0.0", 25)

    rendered = render_html_report(report)

    assert "Showing the 200 most severe findings of 250" in rendered
    assert "Showing the 200 most severe graph nodes of 251" in rendered
    assert "Too large to inline in the dashboard" in rendered
    assert len(rendered.encode("utf-8")) < 2_000_000
