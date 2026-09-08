import json
from pathlib import Path
from typing import Any

from .schema import SecurityGraph

_SET_FIELDS = frozenset(
    {"capabilities", "data_classes", "permissions", "scopes", "tags"}
)


def _sorted_document(graph: SecurityGraph) -> dict[str, Any]:
    document = graph.model_dump(mode="json")
    nodes = sorted(document["nodes"], key=lambda item: item["id"])
    for node in nodes:
        for field in _SET_FIELDS:
            if field in node:
                node[field] = sorted(node[field])
        if "entrypoints" in node:
            node["entrypoints"] = sorted(node["entrypoints"])
        if "model_ids" in node:
            node["model_ids"] = sorted(node["model_ids"])
        if "tool_ids" in node:
            node["tool_ids"] = sorted(node["tool_ids"])
    edges = sorted(document["edges"], key=lambda item: item["id"])
    for edge in edges:
        edge["evidence_refs"] = sorted(edge["evidence_refs"])
    document["nodes"] = nodes
    document["edges"] = edges
    return document


def security_graph_json(graph: SecurityGraph, indent: int = 2) -> str:
    if indent < 0:
        raise ValueError("indent must not be negative")
    return (
        json.dumps(
            _sorted_document(graph),
            ensure_ascii=False,
            indent=indent,
            sort_keys=True,
        )
        + "\n"
    )


def write_security_graph(
    graph: SecurityGraph, destination: Path, indent: int = 2
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(security_graph_json(graph, indent), encoding="utf-8")
