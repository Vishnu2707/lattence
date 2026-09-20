from .app import app
from .targets import (
    OwnedTarget,
    TargetDeclaration,
    TargetDeclarationError,
    load_scope_declaration,
    load_target_declaration,
)


def main() -> None:
    app()


__all__ = [
    "OwnedTarget",
    "TargetDeclaration",
    "TargetDeclarationError",
    "app",
    "load_target_declaration",
    "load_scope_declaration",
    "main",
]
