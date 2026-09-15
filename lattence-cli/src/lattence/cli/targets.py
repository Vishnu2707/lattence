from pathlib import Path, PurePosixPath
from typing import Literal, Self
from urllib.parse import urlsplit

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from yaml import YAMLError

TARGET_DECLARATION_NAME = "lattence.targets.yaml"


class TargetDeclarationError(ValueError):
    pass


class TargetModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class OwnedTarget(TargetModel):
    kind: Literal["project", "url"]
    value: str = Field(min_length=1)

    @model_validator(mode="after")
    def valid_value(self) -> Self:
        if self.kind == "project":
            path = PurePosixPath(self.value)
            if path.is_absolute() or ".." in path.parts or "\\" in self.value:
                raise ValueError("project target must be a relative path")
        else:
            parsed = urlsplit(self.value)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                raise ValueError("URL target must use HTTP or HTTPS")
            if parsed.username or parsed.password:
                raise ValueError("URL target must not contain credentials")
        return self


class TargetDeclaration(TargetModel):
    version: Literal["1"]
    authorization: Literal["owned-or-authorized"]
    targets: list[OwnedTarget] = Field(min_length=1)


def load_target_declaration(root: Path) -> TargetDeclaration:
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as error:
        raise TargetDeclarationError(f"cannot resolve target root: {root}") from error
    declaration_path = resolved_root / TARGET_DECLARATION_NAME
    if declaration_path.is_symlink() or not declaration_path.is_file():
        raise TargetDeclarationError(
            f"attack requires {TARGET_DECLARATION_NAME} in the target root"
        )
    declaration = load_scope_declaration(declaration_path)
    if not any(
        target.kind == "project" and target.value in {".", "./"}
        for target in declaration.targets
    ):
        raise TargetDeclarationError(
            "target declaration must authorize the project root"
        )
    return declaration


def load_scope_declaration(source: Path) -> TargetDeclaration:
    declaration_path = source / TARGET_DECLARATION_NAME if source.is_dir() else source
    if declaration_path.is_symlink() or not declaration_path.is_file():
        raise TargetDeclarationError("declared-scope file not found")
    try:
        document = yaml.safe_load(declaration_path.read_text(encoding="utf-8"))
        declaration = TargetDeclaration.model_validate(document)
    except (OSError, UnicodeError, YAMLError, ValidationError) as error:
        raise TargetDeclarationError(
            f"invalid target declaration: {declaration_path.name}"
        ) from error
    return declaration
