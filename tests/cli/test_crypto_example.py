import json
from pathlib import Path

from lattence.cli import app
from typer.testing import CliRunner

ROOT = Path(__file__).parents[2]
EXAMPLE = ROOT / "examples" / "crypto-migration"
runner = CliRunner()


def test_crypto_example_assesses_and_rolls_back(tmp_path: Path) -> None:
    target = EXAMPLE / "tls.conf"
    original = target.read_bytes()

    assessment = runner.invoke(
        app,
        [
            "pqc",
            "assess",
            str(EXAMPLE),
            "--offline",
            "--json",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )
    chaos = runner.invoke(
        app,
        [
            "crypto",
            "chaos",
            str(EXAMPLE),
            "--offline",
            "--json",
            "--out",
            str(tmp_path),
            "--fail-on",
            "none",
        ],
    )

    assert assessment.exit_code == 0, assessment.output
    assert chaos.exit_code == 0, chaos.output
    assessment_payload = json.loads(assessment.stdout)
    chaos_payload = json.loads(chaos.stdout)
    assert assessment_payload["ml_kem"]["status"] == "already_migrated"
    assert assessment_payload["ml_dsa"]["status"] == "already_migrated"
    assert assessment_payload["hybrid_tls"]["status"] == "valid"
    assert chaos_payload["downgrade"]["status"] == "resistant"
    assert len(chaos_payload["downgrade"]["evidence"]) == 2
    assert target.read_bytes() == original
