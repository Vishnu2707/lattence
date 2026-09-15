from lattence_crypto.pqc import (
    CryptoDependencyGraph,
    CryptoGraphEdge,
    CryptoGraphNode,
    find_quantum_vulnerable_paths,
)


def _node(
    node_id: str, *, status: str | None = None, source: str | None = None
) -> CryptoGraphNode:
    return CryptoGraphNode(
        id=node_id,
        kind="algorithm" if status is not None else "component",
        name=node_id,
        source_path=source,
        quantum_status=status,
    )


def test_finds_direct_and_transitive_quantum_vulnerable_paths() -> None:
    graph = CryptoDependencyGraph(
        nodes=(
            _node("application", source="app.py"),
            _node("certificate", source="server.pem"),
            _node("rsa", status="vulnerable", source="tls.py"),
            _node("ml-kem", status="safe"),
        ),
        edges=(
            CryptoGraphEdge("application", "certificate", "protected_by"),
            CryptoGraphEdge("certificate", "rsa", "protected_by", ("tls.py",)),
        ),
    )

    paths = find_quantum_vulnerable_paths(graph)

    assert [(path.node_ids, path.transitive) for path in paths] == [
        (("application", "certificate", "rsa"), True),
        (("certificate", "rsa"), False),
    ]
    assert paths[0].relationships == ("protected_by", "protected_by")
    assert paths[0].source_paths == ("app.py", "server.pem", "tls.py")


def test_reports_isolated_vulnerable_assets_and_ignores_cycles() -> None:
    graph = CryptoDependencyGraph(
        nodes=(
            _node("rsa", status="vulnerable"),
            _node("left"),
            _node("right"),
        ),
        edges=(
            CryptoGraphEdge("left", "right", "contains"),
            CryptoGraphEdge("right", "left", "contains"),
        ),
    )

    assert find_quantum_vulnerable_paths(graph)[0].node_ids == ("rsa",)
