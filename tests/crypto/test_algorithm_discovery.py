from pathlib import Path

from lattence.discovery import Dependency, inventory_project
from lattence_crypto.discovery import annotate_crypto_references, discover_crypto


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
        "group = X25519 + ML-KEM-768 hybrid\nsignature = ECDSA + ML-DSA-65 hybrid\n",
        encoding="utf-8",
    )

    result = discover_crypto((), tmp_path, inventory_project(tmp_path).files)

    algorithms = {item.algorithm: item for item in result.algorithms}
    assert algorithms["ML-KEM-768"].purpose == "key exchange"
    assert algorithms["ML-KEM-768"].key_size_bits == 768
    assert algorithms["ML-DSA-65"].purpose == "signature"
    assert algorithms["ML-DSA-65"].key_size_bits == 65


def test_generated_reports_do_not_contaminate_repeated_discovery(
    tmp_path: Path,
) -> None:
    (tmp_path / "tls.py").write_text("signature = ECDSA.generate()\n")
    first_inventory = inventory_project(tmp_path)
    first = discover_crypto((), tmp_path, first_inventory.files)
    (tmp_path / "lattence-report.json").write_text(
        '{"generated": "RSA ML-KEM-768 ECDSA"}\n', encoding="utf-8"
    )
    (tmp_path / "lattence-report.html").write_text(
        "<p>RSA ML-DSA-65 ECDSA</p>\n", encoding="utf-8"
    )

    second_inventory = inventory_project(tmp_path)
    second = discover_crypto((), tmp_path, second_inventory.files)

    assert second == first


def test_configured_output_directory_is_excluded_from_discovery(
    tmp_path: Path,
) -> None:
    (tmp_path / "tls.py").write_text("signature = ECDSA.generate()\n")
    output = tmp_path / "artifacts"
    output.mkdir()
    (output / "custom-audit.json").write_text(
        '{"generated": "RSA ML-KEM-768 ECDSA"}\n', encoding="utf-8"
    )

    inventory = inventory_project(tmp_path)
    result = discover_crypto(
        (), tmp_path, inventory.files, excluded_paths=("artifacts/",)
    )

    assert [item.algorithm for item in result.algorithms] == ["ECDSA"]


def test_annotates_explicit_source_and_config_references(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "config" / "tls.yaml").write_text("signature: ECDSA\n")
    (tmp_path / "src" / "app.py").write_text(
        'TLS_CONFIG = "config/tls.yaml"\n', encoding="utf-8"
    )
    inventory = inventory_project(tmp_path)
    discovery = discover_crypto((), tmp_path, inventory.files)

    annotated = annotate_crypto_references(
        tmp_path, inventory.files, discovery.algorithms
    )

    ecdsa = next(item for item in annotated if item.algorithm == "ECDSA")
    assert ecdsa.metadata["referenced_by"] == ["src/app.py"]


def test_records_source_files_that_import_crypto_dependencies(tmp_path: Path) -> None:
    (tmp_path / "tls.py").write_text(
        "from cryptography.hazmat.primitives.asymmetric import rsa\n"
        "key = RSA.generate(key_size=2048)\n",
        encoding="utf-8",
    )
    dependency = Dependency(
        "python", "cryptography", ">=45", "runtime", "pyproject.toml"
    )

    discovery = discover_crypto(
        (dependency,), tmp_path, inventory_project(tmp_path).files
    )

    assert discovery.libraries[0].referenced_by == ("tls.py",)
