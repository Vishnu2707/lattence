from pathlib import Path

import pytest
from lattence_ai.attacks import (
    NATIVE_ATTACK_COUNT,
    AttackCatalogError,
    load_native_attack_catalog,
)

PACK_ROOT = Path(__file__).parents[3] / "lattence-packs" / "attacks"


def test_loads_complete_native_attack_catalog() -> None:
    catalog = load_native_attack_catalog(PACK_ROOT)

    assert len(catalog.rules) == NATIVE_ATTACK_COUNT
    assert catalog.ids == tuple(sorted(catalog.ids))
    assert len(set(catalog.ids)) == NATIVE_ATTACK_COUNT
    assert all(rule.kind == "attack" for rule in catalog.rules)


def test_rejects_incomplete_catalog(tmp_path: Path) -> None:
    with pytest.raises(AttackCatalogError, match="requires 15 rules"):
        load_native_attack_catalog(tmp_path)
