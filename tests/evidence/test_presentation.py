from datetime import UTC, datetime

import pytest
from lattence.evidence import (
    EvidenceBundle,
    Finding,
    build_cross_layer_chain,
    build_security_presentation,
    presentation_json,
)
from lattence.graph import (
    CryptoAlgorithm,
    Dataset,
    Edge,
    Project,
    SecurityGraph,
    Tool,
    find_topology_paths,
)
from pydantic import ValidationError


def _fixture():  # type: ignore[no-untyped-def]
    generated_at = datetime(2026, 1, 1, tzinfo=UTC)
    dataset = Dataset(id="dataset:rag", name="RAG")
    tool = Tool(id="tool:retrieval", name="retrieval")
    crypto = CryptoAlgorithm(
        id="crypto_algorithm:tls12",
        name="TLS 1.2",
        algorithm="TLS 1.2",
        purpose="transport",
        quantum_status="vulnerable",
    )
    nodes = [dataset, tool, crypto]
    graph = SecurityGraph(
        project_id="fixture",
        nodes=nodes,
        edges=[
            Edge(
                id="edge:tool:dataset",
                source_id=tool.id,
                target_id=dataset.id,
                type="accesses",
            ),
            Edge(
                id="edge:tool:crypto",
                source_id=tool.id,
                target_id=crypto.id,
                type="key_exchange",
                evidence_refs=["tls.conf"],
            ),
        ],
        generated_at=generated_at,
    )
    project = Project(
        id="fixture", name="fixture", root=".", scanned_at=generated_at, nodes=nodes
    )
    findings = [
        Finding.model_construct(
            id="LT-AI-002",
            target_node_id=dataset.id,
            evidence=EvidenceBundle.model_construct(id="evidence:ai"),
        ),
        Finding.model_construct(
            id="LT-PQC-203",
            target_node_id=crypto.id,
            evidence=EvidenceBundle.model_construct(id="evidence:pqc"),
        ),
    ]
    path = find_topology_paths(graph, (dataset.id,), (crypto.id,))[0]
    chain = build_cross_layer_chain(
        "LT-AI-002",
        "LT-PQC-203",
        path,
        "A genuine cross-layer chain.",
        ("evidence:ai", "evidence:pqc", "tls.conf"),
    )
    return project, graph, findings, chain


def test_builds_stable_shared_presentation_json() -> None:
    project, graph, findings, chain = _fixture()

    presentation = build_security_presentation(project, graph, findings, [chain])
    rendered = presentation_json(presentation)

    assert rendered == presentation_json(presentation)
    assert presentation.cross_layer_chains[0].hops[0].traversal == "reverse"
    assert presentation.cross_layer_summary.finding_correlations == 1
    assert presentation.cross_layer_summary.distinct_structural_paths == 1
    assert '"finding_correlations": 1' in rendered
    assert '"distinct_structural_paths": 1' in rendered
    assert '"version": "1"' in rendered
    assert rendered.endswith("\n")


def test_summary_collapses_finding_pairs_with_the_same_edge_path() -> None:
    project, graph, findings, chain = _fixture()
    second = chain.model_copy(
        update={
            "id": "cross-layer:second",
            "source_finding_id": "LT-AI-008",
        }
    )
    findings.append(findings[0].model_copy(update={"id": "LT-AI-008"}))

    presentation = build_security_presentation(
        project, graph, findings, [chain, second]
    )

    assert presentation.cross_layer_summary.finding_correlations == 2
    assert presentation.cross_layer_summary.distinct_structural_paths == 1


def test_rejects_altered_or_synthetic_chain_edges() -> None:
    project, graph, findings, chain = _fixture()
    altered_hop = chain.hops[0].model_copy(update={"edge_type": "calls"})
    altered = chain.model_copy(update={"hops": [altered_hop, *chain.hops[1:]]})

    with pytest.raises(ValidationError, match="altered chain edge"):
        build_security_presentation(project, graph, findings, [altered])


def test_rejects_unknown_finding_targets() -> None:
    project, graph, findings, chain = _fixture()
    findings[0] = findings[0].model_copy(update={"target_node_id": "dataset:missing"})

    with pytest.raises(ValidationError, match="unknown finding target"):
        build_security_presentation(project, graph, findings, [chain])
