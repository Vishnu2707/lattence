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
    referenced_by: tuple[str, ...] = ()


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
_GENERATED_ARTIFACT_NAMES = frozenset(
    {
        "lattence-graph.json",
        "lattence-report.html",
        "lattence-report.json",
        "providers.json",
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
    (
        re.compile(r"\bML[-_ ]?KEM(?:[-_ ]?(512|768|1024))?\b", re.I),
        "ML-KEM",
        "key exchange",
    ),
    (
        re.compile(r"\bML[-_ ]?DSA(?:[-_ ]?(44|65|87))?\b", re.I),
        "ML-DSA",
        "signature",
    ),
    (re.compile(r"\bECDSA\b", re.I), "ECDSA", "signature"),
    (re.compile(r"\bEd25519\b", re.I), "Ed25519", "signature"),
    (re.compile(r"\bSHA[-_ ]?256\b", re.I), "SHA-256", "hash"),
    (re.compile(r"\bSHA[-_ ]?1\b", re.I), "SHA-1", "hash"),
    (re.compile(r"\bMD5\b", re.I), "MD5", "hash"),
)
_LIBRARY_IMPORT_NAMES = {
    "cryptography": ("cryptography",),
    "jose": ("jose",),
    "libsodium-wrappers": ("libsodium-wrappers",),
    "node-forge": ("node-forge", "forge"),
    "pycryptodome": ("Crypto",),
    "pyjwt": ("jwt",),
    "pynacl": ("nacl",),
    "tweetnacl": ("tweetnacl",),
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _key_bits(name: str, match: re.Match[str], source: str) -> int | None:
    if name in {"ML-KEM", "ML-DSA"} and match.lastindex:
        captured = match.group(1)
        return int(captured) if captured else None
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
            key_bits = _key_bits(name, match, source)
            algorithm_name = (
                f"{name}-{key_bits}"
                if name in {"ML-KEM", "ML-DSA"} and key_bits is not None
                else name
            )
            algorithms.append(
                CryptoAlgorithm(
                    id=f"crypto_algorithm:{path}:{line}:{_slug(algorithm_name)}",
                    name=algorithm_name,
                    source=SourceRef(path=path, line=line),
                    algorithm=algorithm_name,
                    purpose=purpose,
                    key_size_bits=key_bits,
                    quantum_status="unknown",
                    implementation=path,
                )
            )
    return algorithms


def _is_excluded(path: str, excluded_paths: tuple[str, ...]) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    if normalized.rsplit("/", 1)[-1] in _GENERATED_ARTIFACT_NAMES:
        return True
    for excluded in excluded_paths:
        normalized_excluded = excluded.replace("\\", "/").lstrip("./")
        if normalized_excluded.endswith("/"):
            if normalized.startswith(normalized_excluded):
                return True
        elif normalized == normalized_excluded:
            return True
    return False


def crypto_discovery_files(
    files: tuple[ProjectFile, ...], excluded_paths: tuple[str, ...] = ()
) -> tuple[ProjectFile, ...]:
    return tuple(
        project_file
        for project_file in files
        if not _is_excluded(project_file.path, excluded_paths)
    )


def discover_crypto(
    dependencies: tuple[Dependency, ...],
    root: Path | None = None,
    files: tuple[ProjectFile, ...] = (),
    excluded_paths: tuple[str, ...] = (),
) -> CryptoDiscovery:
    discovered_libraries = {
        (item.name, item.ecosystem, item.source_path)
        for item in dependencies
        if item.name.lower() in _LIBRARIES
    }
    algorithms: list[CryptoAlgorithm] = []
    sources: dict[str, str] = {}
    if root is not None:
        for project_file in crypto_discovery_files(files, excluded_paths):
            try:
                source = (root / project_file.path).read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            sources[project_file.path] = source
            algorithms.extend(_source_algorithms(project_file.path, source))

    libraries = {
        CryptoLibrary(
            name,
            ecosystem,
            source_path,
            tuple(
                sorted(
                    path
                    for path, source in sources.items()
                    if any(
                        re.search(rf"(?<![\w-]){re.escape(alias)}(?![\w-])", source)
                        for alias in _LIBRARY_IMPORT_NAMES.get(name.lower(), (name,))
                    )
                )
            ),
        )
        for name, ecosystem, source_path in discovered_libraries
    }

    unique_algorithms = {item.id: item for item in algorithms}
    return CryptoDiscovery(
        tuple(sorted(libraries)),
        tuple(unique_algorithms[key] for key in sorted(unique_algorithms)),
    )
