import json
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from pydantic import ValidationError
from yaml import YAMLError

from .models import RulePack


class RulePackError(ValueError):
    pass


def _schema() -> dict[str, Any]:
    resource = files("lattence.discovery").joinpath("rule-pack.v1.json")
    value: object = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RulePackError("bundled rule pack schema is not an object")
    return value


def load_rule_pack(path: Path) -> RulePack:
    try:
        loaded: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, YAMLError) as error:
        raise RulePackError(f"cannot read rule pack {path}: {error}") from error

    if not isinstance(loaded, dict):
        raise RulePackError(f"rule pack {path} must contain a mapping")

    validator = Draft202012Validator(_schema())
    errors = sorted(validator.iter_errors(loaded), key=lambda error: list(error.path))
    if errors:
        first_error = errors[0]
        location = ".".join(str(part) for part in first_error.absolute_path) or "root"
        raise RulePackError(
            f"invalid rule pack {path} at {location}: {first_error.message}"
        )

    try:
        return RulePack.model_validate(loaded)
    except ValidationError as error:
        raise RulePackError(f"invalid rule pack {path}: {error}") from error


def load_rule_packs(directory: Path) -> list[RulePack]:
    paths = sorted((*directory.glob("*.yaml"), *directory.glob("*.yml")))
    packs = [load_rule_pack(path) for path in paths]
    seen: set[str] = set()
    for pack in packs:
        if pack.id in seen:
            raise RulePackError(f"duplicate rule pack id: {pack.id}")
        seen.add(pack.id)
    return packs
