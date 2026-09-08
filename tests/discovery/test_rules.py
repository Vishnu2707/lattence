import json
from pathlib import Path

import pytest
from lattence.discovery import RulePackError, load_rule_pack, load_rule_packs

VALID_RULE = """\
version: "1"
id: LT-AI-001
kind: detection
title: Untrusted prompt source
description: Finds an untrusted prompt source.
severity: high
confidence: high
applies_to:
  - agent
match:
  paths:
    - "**/*.txt"
finding:
  message: Untrusted content can reach an agent.
  remediation: Mark external content as data.
"""


def test_load_rule_pack_validates_and_normalizes(tmp_path: Path) -> None:
    path = tmp_path / "rule.yaml"
    path.write_text(VALID_RULE, encoding="utf-8")

    rule = load_rule_pack(path)

    assert rule.id == "LT-AI-001"
    assert rule.match.paths == ["**/*.txt"]
    assert rule.tests == []


def test_load_rule_pack_rejects_unknown_fields(tmp_path: Path) -> None:
    path = tmp_path / "rule.yaml"
    path.write_text(f"{VALID_RULE}unknown: true\n", encoding="utf-8")

    with pytest.raises(RulePackError, match="Additional properties"):
        load_rule_pack(path)


def test_load_rule_pack_rejects_non_mapping(tmp_path: Path) -> None:
    path = tmp_path / "rule.yaml"
    path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(RulePackError, match="must contain a mapping"):
        load_rule_pack(path)


def test_load_rule_packs_is_sorted_and_rejects_duplicate_ids(
    tmp_path: Path,
) -> None:
    (tmp_path / "b.yml").write_text(VALID_RULE, encoding="utf-8")
    second = VALID_RULE.replace("LT-AI-001", "LT-AI-002")
    (tmp_path / "a.yaml").write_text(second, encoding="utf-8")

    assert [rule.id for rule in load_rule_packs(tmp_path)] == [
        "LT-AI-002",
        "LT-AI-001",
    ]

    (tmp_path / "a.yaml").write_text(VALID_RULE, encoding="utf-8")
    with pytest.raises(RulePackError, match="duplicate rule pack id"):
        load_rule_packs(tmp_path)


def test_bundled_schema_matches_documented_contract() -> None:
    root = Path(__file__).parents[2]
    documented = json.loads(
        (root / "docs/schemas/rule-pack.v1.json").read_text(encoding="utf-8")
    )
    bundled = json.loads(
        (root / "lattence-core/src/lattence/discovery/rule-pack.v1.json").read_text(
            encoding="utf-8"
        )
    )

    assert bundled == documented
