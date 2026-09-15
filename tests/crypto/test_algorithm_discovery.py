from pathlib import Path

from lattence.discovery import Dependency, inventory_project
from lattence_crypto.discovery import discover_crypto


def test_discovers_crypto_libraries_and_algorithms(tmp_path: Path) -> None:
    (tmp_path / "crypto.py").write_text(
        "rsa.generate_private_key(public_exponent=65537, key_size=2048)\n"
        "digest = SHA256(data)\n"
        "cipher = AES_256_GCM(key)\n",
        encoding="utf-8",
    )
    dependencies = (
        Dependency("python", "cryptography", ">=45", "runtime", "pyproject.toml"),
        Dependency("python", "requests", ">=2", "runtime", "pyproject.toml"),
    )

    result = discover_crypto(dependencies, tmp_path, inventory_project(tmp_path).files)

    assert [library.name for library in result.libraries] == ["cryptography"]
    assert {item.algorithm for item in result.algorithms} == {
        "AES-GCM",
        "RSA",
        "SHA-256",
    }
    rsa_algorithm = next(item for item in result.algorithms if item.algorithm == "RSA")
    assert rsa_algorithm.key_size_bits == 2048
    assert all(item.quantum_status == "unknown" for item in result.algorithms)


def test_unknown_dependencies_and_plain_source_produce_no_results(
    tmp_path: Path,
) -> None:
    (tmp_path / "plain.py").write_text("value = 1\n", encoding="utf-8")
    dependencies = (
        Dependency("python", "requests", ">=2", "runtime", "pyproject.toml"),
    )

    result = discover_crypto(dependencies, tmp_path, inventory_project(tmp_path).files)

    assert result.libraries == ()
    assert result.algorithms == ()


def test_discovers_ml_kem_and_ml_dsa_parameter_sets(tmp_path: Path) -> None:
    (tmp_path / "tls.conf").write_text(
        "group = X25519 + ML-KEM-768 hybrid\n"
        "signature = ECDSA + ML-DSA-65 hybrid\n",
        encoding="utf-8",
    )

    result = discover_crypto((), tmp_path, inventory_project(tmp_path).files)

    algorithms = {item.algorithm: item for item in result.algorithms}
    assert algorithms["ML-KEM-768"].purpose == "key exchange"
    assert algorithms["ML-KEM-768"].key_size_bits == 768
    assert algorithms["ML-DSA-65"].purpose == "signature"
    assert algorithms["ML-DSA-65"].key_size_bits == 65
