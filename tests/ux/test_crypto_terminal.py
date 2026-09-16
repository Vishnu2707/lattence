from pathlib import Path

from lattence.cli.crypto_workflow import create_crypto_assessment
from lattence.cli.presentation import render_crypto_assessment


def _project(root: Path) -> None:
    (root / "tls.py").write_text(
        "minimum = ssl.TLSVersion.TLSv1_3\n"
        "group = X25519 + ML-KEM-768 hybrid\n"
        "signature = ECDSA + ML-DSA-65 hybrid\n",
        encoding="utf-8",
    )


def test_crypto_terminal_renders_all_flagship_sections(tmp_path: Path) -> None:
    _project(tmp_path)
    assessment = create_crypto_assessment(tmp_path)

    rendered = render_crypto_assessment(assessment, tmp_path)

    assert "CRYPTO GRAPH" in rendered
    assert "MIGRATION TESTS" in rendered
    assert "HYBRID TLS" in rendered
    assert "CRYPTO AGILITY" in rendered
    assert "DOWNGRADE VALIDATION" in rendered
    assert "ML-KEM" in rendered
    assert "ML-DSA" in rendered
    assert "Isolated vulnerable assets" in rendered
    assert "Traversable paths" in rendered
    assert "Vulnerable paths" not in rendered
    assert "\x1b[" not in rendered


def test_crypto_terminal_color_mode_preserves_text_signals(tmp_path: Path) -> None:
    _project(tmp_path)
    assessment = create_crypto_assessment(tmp_path)

    rendered = render_crypto_assessment(assessment, tmp_path, color=True)

    assert "\x1b[" in rendered
    assert "CRYPTO GRAPH" in rendered
    assert assessment.hybrid_tls.status.upper() in rendered
