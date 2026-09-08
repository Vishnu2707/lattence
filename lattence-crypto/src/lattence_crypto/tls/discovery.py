import re
from dataclasses import dataclass
from pathlib import Path

from cryptography import x509
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.asymmetric import dsa, ec, ed448, ed25519, rsa
from lattence.discovery import ProjectFile
from lattence.graph import Certificate, CryptoAlgorithm, SourceRef

_CERTIFICATE_SUFFIXES = frozenset({".cer", ".crt", ".pem"})
_TLS_PATTERNS = (
    (re.compile(r"TLS(?:v|_VERSION_?)?1[_\.]?3", re.IGNORECASE), "TLS 1.3"),
    (re.compile(r"TLS(?:v|_VERSION_?)?1[_\.]?2", re.IGNORECASE), "TLS 1.2"),
)
_KEY_EXCHANGE_PATTERNS = (
    (re.compile(r"(?<![A-Za-z0-9])X25519(?![0-9])", re.IGNORECASE), "X25519", 255),
    (re.compile(r"(?<![A-Za-z0-9])X448(?![0-9])", re.IGNORECASE), "X448", 448),
    (re.compile(r"\bECDHE\b", re.IGNORECASE), "ECDHE", None),
    (re.compile(r"\bDHE\b", re.IGNORECASE), "DHE", None),
)


@dataclass(frozen=True)
class TLSDiscovery:
    certificates: tuple[Certificate, ...]
    algorithms: tuple[CryptoAlgorithm, ...]
    errors: tuple[str, ...]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _load_certificate(data: bytes) -> x509.Certificate:
    if b"-----BEGIN CERTIFICATE-----" in data:
        return x509.load_pem_x509_certificate(data)
    return x509.load_der_x509_certificate(data)


def _public_key_details(certificate: x509.Certificate) -> tuple[str, int | None]:
    public_key = certificate.public_key()
    if isinstance(public_key, rsa.RSAPublicKey):
        return "RSA", public_key.key_size
    if isinstance(public_key, ec.EllipticCurvePublicKey):
        return "EC", public_key.key_size
    if isinstance(public_key, dsa.DSAPublicKey):
        return "DSA", public_key.key_size
    if isinstance(public_key, ed25519.Ed25519PublicKey):
        return "Ed25519", 255
    if isinstance(public_key, ed448.Ed448PublicKey):
        return "Ed448", 448
    return type(public_key).__name__, None


def _signature_algorithm(certificate: x509.Certificate) -> str:
    try:
        algorithm = certificate.signature_hash_algorithm
    except UnsupportedAlgorithm:
        algorithm = None
    if algorithm is not None:
        return algorithm.name
    return certificate.signature_algorithm_oid.dotted_string


def _certificate(path: str, value: x509.Certificate) -> Certificate:
    key_algorithm, key_bits = _public_key_details(value)
    serial_number = format(value.serial_number, "x")
    return Certificate(
        id=f"certificate:{path}:{serial_number}",
        name=value.subject.rfc4514_string() or Path(path).name,
        source=SourceRef(path=path),
        subject=value.subject.rfc4514_string() or None,
        issuer=value.issuer.rfc4514_string() or None,
        serial_number=serial_number,
        not_before=value.not_valid_before_utc,
        not_after=value.not_valid_after_utc,
        signature_algorithm=_signature_algorithm(value),
        public_key_algorithm=key_algorithm,
        public_key_bits=key_bits,
        file_path=path,
    )


def _configuration_algorithms(path: str, source: str) -> list[CryptoAlgorithm]:
    algorithms: list[CryptoAlgorithm] = []
    for pattern, name in _TLS_PATTERNS:
        match = pattern.search(source)
        if match:
            algorithms.append(
                _algorithm(path, source, match.start(), name, "transport")
            )
    for pattern, name, bits in _KEY_EXCHANGE_PATTERNS:
        match = pattern.search(source)
        if match:
            algorithms.append(
                _algorithm(path, source, match.start(), name, "key exchange", bits)
            )
    return algorithms


def _algorithm(
    path: str,
    source: str,
    offset: int,
    name: str,
    purpose: str,
    bits: int | None = None,
) -> CryptoAlgorithm:
    line = source.count("\n", 0, offset) + 1
    return CryptoAlgorithm(
        id=f"crypto_algorithm:{path}:{line}:{_slug(name)}",
        name=name,
        source=SourceRef(path=path, line=line),
        algorithm=name,
        purpose=purpose,
        key_size_bits=bits,
        quantum_status="unknown",
        implementation=path,
    )


def discover_tls(root: Path, files: tuple[ProjectFile, ...]) -> TLSDiscovery:
    certificates: list[Certificate] = []
    algorithms: list[CryptoAlgorithm] = []
    errors: list[str] = []
    for project_file in files:
        path = project_file.path
        absolute_path = root / path
        if absolute_path.suffix.lower() in _CERTIFICATE_SUFFIXES:
            try:
                certificates.append(
                    _certificate(path, _load_certificate(absolute_path.read_bytes()))
                )
            except (OSError, ValueError):
                errors.append(f"cannot parse certificate: {path}")
            continue
        try:
            source = absolute_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        algorithms.extend(_configuration_algorithms(path, source))

    unique_algorithms = {algorithm.id: algorithm for algorithm in algorithms}
    return TLSDiscovery(
        tuple(sorted(certificates, key=lambda item: item.id)),
        tuple(unique_algorithms[key] for key in sorted(unique_algorithms)),
        tuple(sorted(errors)),
    )
