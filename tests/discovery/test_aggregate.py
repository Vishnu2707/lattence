from datetime import UTC, datetime
from pathlib import Path

import pytest
from lattence.discovery import DiscoveryError, discover_project
from lattence.graph import Tool


def _write_rule(root: Path) -> Path:
    rule_root = root / "rules"
    category = rule_root / "frameworks"
    category.mkdir(parents=True)
    (category / "fixture.yaml").write_text(
        """\
version: "1"
id: LT-FIXTURE-001
kind: detection
title: Fixture framework
description: Detect the fixture framework.
severity: info
confidence: high
applies_to: [application]
match:
  dependencies: [fixture]
finding:
  message: Fixture framework detected.
  remediation: Review the framework configuration.
""",
        encoding="utf-8",
    )
    return rule_root


def test_aggregates_nodes_with_stable_order_and_ids(tmp_path: Path) -> None:
    rule_root = _write_rule(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname="fixture"\nversion="1"\ndependencies=["fixture"]\n',
        encoding="utf-8",
    )
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    extra = Tool(id="tool:extra", name="extra")

    first = discover_project(tmp_path, rule_root, (extra, extra), timestamp)
    second = discover_project(tmp_path, rule_root, (extra,), timestamp)

    assert first.project == second.project
    assert first.project.id.startswith("project:")
    assert [node.id for node in first.project.nodes] == sorted(
        node.id for node in first.project.nodes
    )
    assert [node.id for node in first.project.nodes].count("tool:extra") == 1


def test_rejects_conflicting_duplicate_node_ids(tmp_path: Path) -> None:
    rule_root = _write_rule(tmp_path)
    first = Tool(id="tool:duplicate", name="first")
    second = Tool(id="tool:duplicate", name="second")

    with pytest.raises(DiscoveryError, match="conflicting discovery node id"):
        discover_project(tmp_path, rule_root, (first, second))
