import json
from pathlib import Path

from lattence.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def _crypto_project(root: Path, *, require_pqc: bool = False) -> str:
    original = (
        "minimum_version = ssl.TLSVersion.TLSv1_3\n"
        "key_exchange = X25519 + ML-KEM-768 hybrid\n"
        "signature = ECDSA + ML-DSA-65 hybrid\n"
        f"require_pqc = {'true' if require_pqc else 'false'}\n"
    )
    (root / "tls.conf").write_text(original, encoding="utf-8")
    (root / "lattence.targets.yaml").write_text(
        """\
version: "1"
authorization: owned-or-authorized
targets:
  - kind: project
    value: "."
  - kind: project
    value: "tls.conf"
""",
        encoding="utf-8",
    )
    return original


def test_pqc_assess_emits_full_crypto_assessment(tmp_path: Path) -> None:
    _crypto_project(tmp_path)

    result = runner.invoke(
        app,
        [
            "pqc",
            "assess",
            str(tmp_path),
            "--json",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["ml_kem"]["status"] == "already_migrated"
    assert payload["ml_dsa"]["status"] == "already_migrated"
    assert payload["hybrid_tls"]["status"] == "valid"
    assert "components" in payload["agility"]
    assert "isolated_assets" in payload["quantum_exposure"]
    assert "paths" in payload["quantum_exposure"]
    assert "vulnerable_paths" not in payload
    assert (tmp_path / "lattence-report.json").is_file()


def test_repeated_pqc_assessment_has_identical_crypto_counts(tmp_path: Path) -> None:
    _crypto_project(tmp_path)
    command = [
        "pqc",
        "assess",
        str(tmp_path),
        "--json",
        "--out",
        str(tmp_path),
        "--fail-on",
        "none",
    ]

    first = runner.invoke(app, command)
    second = runner.invoke(app, command)

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    first_payload = json.loads(first.stdout)
    second_payload = json.loads(second.stdout)
    assert len(first_payload["crypto_graph"]["nodes"]) == len(
        second_payload["crypto_graph"]["nodes"]
    )
    assert len(first_payload["crypto_graph"]["edges"]) == len(
        second_payload["crypto_graph"]["edges"]
    )
    assert first_payload["quantum_exposure"] == second_payload["quantum_exposure"]


def test_crypto_chaos_requires_consent_and_restores_target(tmp_path: Path) -> None:
    (tmp_path / "tls.conf").write_text("ML-KEM-768\n", encoding="utf-8")
    refused = runner.invoke(app, ["crypto", "chaos", str(tmp_path)])
    assert refused.exit_code == 2
    assert "requires lattence.targets.yaml" in refused.output

    original = _crypto_project(tmp_path)
    result = runner.invoke(
        app,
        [
            "crypto",
            "chaos",
            str(tmp_path),
            "--json",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["downgrade"]["status"] == "vulnerable"
    assert len(payload["downgrade"]["evidence"]) == 2
    assert (tmp_path / "tls.conf").read_text(encoding="utf-8") == original


def test_crypto_chaos_reports_resistant_enforcement(tmp_path: Path) -> None:
    _crypto_project(tmp_path, require_pqc=True)

    result = runner.invoke(
        app,
        [
            "crypto",
            "chaos",
            str(tmp_path),
            "--json",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["downgrade"]["status"] == "resistant"
