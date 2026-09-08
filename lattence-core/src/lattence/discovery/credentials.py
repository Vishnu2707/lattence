import re
from dataclasses import dataclass
from pathlib import Path

from lattence.graph import Identity, Secret, SourceRef

from .inventory import ProjectFile
from .javascript_syntax import JavaScriptSyntax
from .python_syntax import PythonSyntax

_SECRET_TERMS = re.compile(
    r"(?:^|_)(?:api_?key|credential|password|private_?key|secret|token)(?:$|_)",
    re.IGNORECASE,
)
_IDENTITY_TERMS = {
    "oauth": ("oauth", "authlib"),
    "jwt": ("jwt", "jose", "jwk"),
}


@dataclass(frozen=True)
class IdentityDiscovery:
    secrets: tuple[Secret, ...]
    identities: tuple[Identity, ...]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _secret(path: str, line: int, name: str, kind: str = "credential") -> Secret:
    return Secret(
        id=f"secret:{path}:{line}:{_slug(name)}",
        name=name,
        source=SourceRef(path=path, line=line),
        kind=kind,
        location=f"{path}:{line}",
        exposed_value=False,
        environment_name=name if path.startswith(".env") else None,
    )


def _environment_secrets(root: Path, files: tuple[ProjectFile, ...]) -> list[Secret]:
    secrets: list[Secret] = []
    for project_file in files:
        if not Path(project_file.path).name.startswith(".env"):
            continue
        try:
            lines = (root / project_file.path).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue
        for line_number, line in enumerate(lines, start=1):
            name, separator, _value = line.partition("=")
            name = name.strip().removeprefix("export ").strip()
            if separator and name and _SECRET_TERMS.search(name):
                secrets.append(_secret(project_file.path, line_number, name))
    return secrets


def _syntax_values(
    python_files: tuple[PythonSyntax, ...],
    javascript_files: tuple[JavaScriptSyntax, ...],
) -> list[tuple[str, int, str]]:
    values: list[tuple[str, int, str]] = []
    for python_syntax in python_files:
        values.extend(
            (python_syntax.path, item.location.line, item.module)
            for item in python_syntax.imports
        )
        values.extend(
            (python_syntax.path, item.location.line, item.function)
            for item in python_syntax.calls
        )
    for javascript_syntax in javascript_files:
        values.extend(
            (javascript_syntax.path, item.location.line, item.module)
            for item in javascript_syntax.imports
        )
        values.extend(
            (javascript_syntax.path, item.location.line, item.function)
            for item in javascript_syntax.calls
        )
    return values


def detect_identities(
    root: Path,
    files: tuple[ProjectFile, ...],
    python_files: tuple[PythonSyntax, ...] = (),
    javascript_files: tuple[JavaScriptSyntax, ...] = (),
) -> IdentityDiscovery:
    secrets = _environment_secrets(root, files)
    for syntax in python_files:
        secrets.extend(
            _secret(syntax.path, item.location.line, item.target)
            for item in syntax.assignments
            if _SECRET_TERMS.search(item.target)
        )

    identities: list[Identity] = []
    for path, line, value in _syntax_values(python_files, javascript_files):
        lowered = value.lower()
        for kind, terms in _IDENTITY_TERMS.items():
            if not any(term in lowered for term in terms):
                continue
            identities.append(
                Identity(
                    id=f"identity:{kind}:{path}:{line}",
                    name=f"{kind.upper()} identity",
                    source=SourceRef(path=path, line=line),
                    kind=kind,
                )
            )

    unique_secrets = {item.id: item for item in secrets}
    unique_identities = {item.id: item for item in identities}
    return IdentityDiscovery(
        tuple(unique_secrets[key] for key in sorted(unique_secrets)),
        tuple(unique_identities[key] for key in sorted(unique_identities)),
    )
