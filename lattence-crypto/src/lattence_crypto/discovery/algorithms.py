import re
from dataclasses import dataclass
from pathlib import Path

from lattence.discovery import Dependency, ProjectFile
from lattence.graph import CryptoAlgorithm, SourceRef


@dataclass(frozen=True, order=True)
class CryptoLibrary:
    name: str
    ecosystem: str
    source_path: str


@dataclass(frozen=True)
class CryptoDiscovery:
    libraries: tuple[CryptoLibrary, ...]
    algorithms: tuple[CryptoAlgorithm, ...]


_LIBRARIES = frozenset(
    {
        "bcrypt",
        "cryptography",
        "jose",
        "libsodium-wrappers",
        "node-forge",
        "passlib",
        "pycryptodome",
        "pyjwt",
        "pynacl",
        "tweetnacl",
    }
)
_ALGORITHM_PATTERNS = (
    (
        re.compile(r"\bAES(?:[-_ ]?(128|192|256))?[-_ ]?GCM\b", re.I),
        "AES-GCM",
        "encryption",
    ),
    (re.compile(r"\bChaCha20(?:Poly1305)?\b", re.I), "ChaCha20-Poly1305", "encryption"),
    (re.compile(r"\bRSA\b", re.I), "RSA", "public-key encryption"),
    (re.compile(r"\bECDSA\b", re.I), "ECDSA", "signature"),
    (re.compile(r"\bEd25519\b", re.I), "Ed25519", "signature"),
    (re.compile(r"\bSHA[-_ ]?256\b", re.I), "SHA-256", "hash"),
    (re.compile(r"\bSHA[-_ ]?1\b", re.I), "SHA-1", "hash"),
    (re.compile(r"\bMD5\b", re.I), "MD5", "hash"),
)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _key_bits(name: str, match: re.Match[str], source: str) -> int | None:
    if name == "AES-GCM" and match.lastindex:
        captured = match.group(1)
        return int(captured) if captured else None
    if name != "RSA":
        return None
    nearby = source[match.end() : match.end() + 120]
    size = re.search(r"(?:key_size\s*=\s*|[-_ ])(\d{4})\b", nearby)
    return int(size.group(1)) if size else None


def _source_algorithms(path: str, source: str) -> list[CryptoAlgorithm]:
    algorithms: list[CryptoAlgorithm] = []
    for pattern, name, purpose in _ALGORITHM_PATTERNS:
        for match in pattern.finditer(source):
            line = source.count("\n", 0, match.start()) + 1
            algorithms.append(
                CryptoAlgorithm(
                    id=f"crypto_algorithm:{path}:{line}:{_slug(name)}",
                    name=name,
                    source=SourceRef(path=path, line=line),
                    algorithm=name,
                    purpose=purpose,
                    key_size_bits=_key_bits(name, match, source),
                    quantum_status="unknown",
                    implementation=path,
                )
            )
    return algorithms


def discover_crypto(
    dependencies: tuple[Dependency, ...],
    root: Path | None = None,
    files: tuple[ProjectFile, ...] = (),
) -> CryptoDiscovery:
    libraries = {
        CryptoLibrary(item.name, item.ecosystem, item.source_path)
        for item in dependencies
        if item.name.lower() in _LIBRARIES
    }
    algorithms: list[CryptoAlgorithm] = []
    if root is not None:
        for project_file in files:
            try:
                source = (root / project_file.path).read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            algorithms.extend(_source_algorithms(project_file.path, source))

    unique_algorithms = {item.id: item for item in algorithms}
    return CryptoDiscovery(
        tuple(sorted(libraries)),
        tuple(unique_algorithms[key] for key in sorted(unique_algorithms)),
    )
