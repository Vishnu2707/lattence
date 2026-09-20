from pathlib import Path

from lattence.cli.crypto_workflow import create_crypto_assessment
from lattence.cli.workflow import create_report
from lattence_ai.attacks import correlate_cross_layer_findings

EXAMPLE = Path(__file__).parents[3] / "examples" / "vulnerable-agent"
DATASET_ID = "dataset:rag-pipeline:app.py:15"
TOOL_ID = "tool:app.py:delete_customer_record"


def test_correlates_real_findings_over_discovered_vulnerable_graph() -> None:
    report = create_report(EXAMPLE)
    crypto = create_crypto_assessment(EXAMPLE, base_report=report)
    findings = (*report.findings, *crypto.report.findings)

    correlations = correlate_cross_layer_findings(
        report.graph,
        findings,
        max_depth=4,
    )

    correlation = next(
        item
        for item in correlations
        if item.source_finding_id == "LT-AI-002"
        and item.crypto_finding_id == "LT-PQC-203"
        and item.path.node_ids[0] == DATASET_ID
    )
    assert correlation.path.node_ids == (
        DATASET_ID,
        TOOL_ID,
        "crypto_algorithm:crypto_config.py:7:tls-1-2",
    )
    assert [hop.edge_type for hop in correlation.path.hops] == [
        "accesses",
        "key_exchange",
    ]
    assert [hop.traversal for hop in correlation.path.hops] == [
        "reverse",
        "forward",
    ]
    assert {"app.py", "crypto_config.py"}.issubset(correlation.evidence_refs)

    edge_by_id = {edge.id: edge for edge in report.graph.edges}
    for hop in correlation.path.hops:
        edge = edge_by_id[hop.edge_id]
        assert (hop.source_id, hop.target_id, hop.edge_type) == (
            edge.source_id,
            edge.target_id,
            edge.type,
        )

    connected_crypto_nodes = {
        edge.target_id
        for edge in report.graph.edges
        if edge.source_id == TOOL_ID
        and edge.type in {"key_exchange", "protected_by"}
        and edge.target_id.startswith("crypto_algorithm:")
    }
    assert len(connected_crypto_nodes) == 7
