from pathlib import Path

from lattence.discovery import (
    detect_identities,
    inventory_project,
    parse_javascript_source,
    parse_python_source,
)


def test_detects_secret_names_without_retaining_values(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text(
        "API_KEY=sensitive-value\nPUBLIC_NAME=visible\n", encoding="utf-8"
    )
    syntax = parse_python_source(
        "service_token = 'another-sensitive-value'\n", "src/config.py"
    )
    inventory = inventory_project(tmp_path)

    result = detect_identities(tmp_path, inventory.files, (syntax,))

    assert {secret.name for secret in result.secrets} == {"API_KEY", "service_token"}
    assert all(not secret.exposed_value for secret in result.secrets)
    rendered = repr(result)
    assert "sensitive-value" not in rendered
    assert "another-sensitive-value" not in rendered


def test_detects_oauth_and_jwt_identities() -> None:
    python = parse_python_source("import jwt\noauth.authorize()\n", "auth.py")
    javascript = parse_javascript_source(
        'import token from "jose";\nverifyJwt();\n', "auth.ts"
    )

    result = detect_identities(Path("."), (), (python,), (javascript,))

    assert {identity.kind for identity in result.identities} == {"oauth", "jwt"}
    assert all(identity.provider is None for identity in result.identities)


def test_plain_source_produces_no_identity_nodes(tmp_path: Path) -> None:
    syntax = parse_python_source("value = 1\n", "plain.py")

    result = detect_identities(tmp_path, (), (syntax,))

    assert result.secrets == ()
    assert result.identities == ()
