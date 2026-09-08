from dataclasses import dataclass
from pathlib import Path

from lattence.discovery import RulePack, RulePackError, load_rule_pack

NATIVE_ATTACK_COUNT = 15


class AttackCatalogError(ValueError):
    pass


@dataclass(frozen=True)
class NativeAttackCatalog:
    rules: tuple[RulePack, ...]

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(rule.id for rule in self.rules)


def load_native_attack_catalog(root: Path) -> NativeAttackCatalog:
    if not root.is_dir():
        raise AttackCatalogError(f"attack catalog directory does not exist: {root}")
    try:
        rules = tuple(
            sorted(
                (load_rule_pack(path) for path in root.rglob("*.yaml")),
                key=lambda item: item.id,
            )
        )
    except RulePackError as error:
        raise AttackCatalogError("cannot load native attack catalog") from error
    if len(rules) != NATIVE_ATTACK_COUNT:
        count = len(rules)
        raise AttackCatalogError(
            f"native attack catalog requires {NATIVE_ATTACK_COUNT} rules, found {count}"
        )
    rule_ids = [rule.id for rule in rules]
    duplicate = next(
        (rule_id for rule_id in set(rule_ids) if rule_ids.count(rule_id) > 1), None
    )
    if duplicate is not None:
        raise AttackCatalogError(f"duplicate native attack id: {duplicate}")
    if any(rule.kind != "attack" for rule in rules):
        raise AttackCatalogError("native attack catalog contains a non-attack rule")
    return NativeAttackCatalog(rules)
