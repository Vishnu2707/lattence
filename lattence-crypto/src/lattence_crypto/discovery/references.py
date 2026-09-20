import re
from pathlib import Path

from lattence.discovery import ProjectFile
from lattence.graph import Certificate, CryptoAlgorithm

type CryptoAsset = Certificate | CryptoAlgorithm

_REFERENCE_SUFFIXES = frozenset(
    {
        ".c",
        ".cc",
        ".cpp",
        ".cs",
        ".go",
        ".h",
        ".hpp",
        ".java",
        ".js",
        ".jsx",
        ".kt",
        ".php",
        ".py",
        ".rb",
        ".rs",
        ".sh",
        ".swift",
        ".ts",
        ".tsx",
    }
)


def _references(source: str, path: str) -> bool:
    asset_source = Path(path)
    if path in source or asset_source.name in source:
        return True
    module = asset_source.with_suffix("").as_posix().replace("/", ".")
    import_pattern = re.compile(rf"\b(?:from|import)\s+{re.escape(module)}(?:\b|\.)")
    return import_pattern.search(source) is not None


def annotate_crypto_references(
    root: Path,
    files: tuple[ProjectFile, ...],
    assets: tuple[CryptoAsset, ...],
) -> tuple[CryptoAsset, ...]:
    """Record code files that explicitly name a crypto asset's source file."""
    sources: dict[str, str] = {}
    for project_file in files:
        if Path(project_file.path).suffix.lower() not in _REFERENCE_SUFFIXES:
            continue
        try:
            sources[project_file.path] = (root / project_file.path).read_text(
                encoding="utf-8"
            )
        except (OSError, UnicodeError):
            continue

    annotated: list[CryptoAsset] = []
    for asset in assets:
        if asset.source is None:
            annotated.append(asset)
            continue
        asset_path = asset.source.path
        references = sorted(
            path
            for path, source in sources.items()
            if path != asset_path and _references(source, asset_path)
        )
        if not references:
            annotated.append(asset)
            continue
        metadata = {**asset.metadata, "referenced_by": references}
        annotated.append(asset.model_copy(update={"metadata": metadata}))
    return tuple(annotated)
