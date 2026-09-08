from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from lattence.discovery import inventory_project
from lattence_crypto.tls import discover_tls


def _write_certificate(path: Path) -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "local.test")])
    now = datetime.now(UTC)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(42)
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))


def test_discovers_certificate_tls_version_and_key_exchange(tmp_path: Path) -> None:
    _write_certificate(tmp_path / "server.crt")
    (tmp_path / "tls.py").write_text(
        "minimum_version = ssl.TLSVersion.TLSv1_3\nkey = X25519PrivateKey.generate()\n",
        encoding="utf-8",
    )

    inventory = inventory_project(tmp_path)
    result = discover_tls(tmp_path, inventory.files)

    certificate = result.certificates[0]
    assert certificate.subject == "CN=local.test"
    assert certificate.issuer == "CN=local.test"
    assert certificate.serial_number == "2a"
    assert certificate.signature_algorithm == "sha256"
    assert certificate.public_key_algorithm == "RSA"
    assert certificate.public_key_bits == 2048
    assert certificate.file_path == "server.crt"
    assert {item.algorithm for item in result.algorithms} == {"TLS 1.3", "X25519"}
    assert result.errors == ()


def test_invalid_certificate_is_reported_without_content(tmp_path: Path) -> None:
    (tmp_path / "bad.pem").write_text("private material", encoding="utf-8")

    result = discover_tls(tmp_path, inventory_project(tmp_path).files)

    assert result.certificates == ()
    assert result.errors == ("cannot parse certificate: bad.pem",)
    assert "private material" not in repr(result)


def test_plain_project_has_no_tls_assets(tmp_path: Path) -> None:
    (tmp_path / "plain.py").write_text("value = 1\n", encoding="utf-8")

    result = discover_tls(tmp_path, inventory_project(tmp_path).files)

    assert result.certificates == ()
    assert result.algorithms == ()
    assert result.errors == ()
