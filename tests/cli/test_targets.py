from pathlib import Path

import pytest
from lattence.cli import TargetDeclarationError, load_target_declaration


def test_loads_owned_project_declaration(tmp_path: Path) -> None:
    (tmp_path / "lattence.targets.yaml").write_text(
        """\
version: "1"
authorization: owned-or-authorized
targets:
  - kind: project
    value: "."
""",
        encoding="utf-8",
    )

    declaration = load_target_declaration(tmp_path)

    assert declaration.authorization == "owned-or-authorized"
    assert declaration.targets[0].value == "."


def test_refuses_missing_and_unscoped_declarations(tmp_path: Path) -> None:
    with pytest.raises(TargetDeclarationError, match="attack requires"):
        load_target_declaration(tmp_path)

    (tmp_path / "lattence.targets.yaml").write_text(
        """\
version: "1"
authorization: owned-or-authorized
targets:
  - kind: url
    value: https://example.invalid
""",
        encoding="utf-8",
    )
    with pytest.raises(TargetDeclarationError, match="authorize the project root"):
        load_target_declaration(tmp_path)


def test_invalid_declaration_error_does_not_echo_content(tmp_path: Path) -> None:
    (tmp_path / "lattence.targets.yaml").write_text(
        "authorization: sensitive-value\n", encoding="utf-8"
    )

    with pytest.raises(TargetDeclarationError) as captured:
        load_target_declaration(tmp_path)

    assert "sensitive-value" not in str(captured.value)
