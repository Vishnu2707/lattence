from .app import app
from .targets import (
    OwnedTarget,
    TargetDeclaration,
    TargetDeclarationError,
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
    "main",
]
