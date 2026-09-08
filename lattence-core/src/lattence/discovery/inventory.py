import os
from dataclasses import dataclass
from pathlib import Path

from pathspec import PathSpec

DEFAULT_EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".next",
        ".nox",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "coverage",
        "dist",
        "htmlcov",
        "node_modules",
        "out",
        "site",
        "target",
    }
)


class InventoryError(ValueError):
    pass


@dataclass(frozen=True)
class InventoryOptions:
    max_file_bytes: int = 2_000_000
    max_files: int = 100_000
    use_gitignore: bool = True
    excluded_directories: frozenset[str] = DEFAULT_EXCLUDED_DIRECTORIES

    def __post_init__(self) -> None:
        if self.max_file_bytes < 1:
            raise InventoryError("max_file_bytes must be positive")
        if self.max_files < 1:
            raise InventoryError("max_files must be positive")


@dataclass(frozen=True, order=True)
class ProjectFile:
    path: str
    size_bytes: int


@dataclass(frozen=True, order=True)
class SkippedFile:
    path: str
    reason: str


@dataclass(frozen=True)
class ProjectInventory:
    root: Path
    files: tuple[ProjectFile, ...]
    skipped: tuple[SkippedFile, ...]


def _load_ignore(root: Path, enabled: bool) -> PathSpec:
    ignore_file = root / ".gitignore"
    if not enabled or not ignore_file.is_file():
        return PathSpec.from_lines("gitwildmatch", ())
    try:
        lines = ignore_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise InventoryError(f"cannot read {ignore_file}: {error}") from error
    return PathSpec.from_lines("gitwildmatch", lines)


def inventory_project(
    root: Path, options: InventoryOptions | None = None
) -> ProjectInventory:
    options = options or InventoryOptions()
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as error:
        raise InventoryError(f"cannot resolve project root {root}: {error}") from error
    if not resolved_root.is_dir():
        raise InventoryError(f"project root is not a directory: {root}")

    ignore = _load_ignore(resolved_root, options.use_gitignore)
    files: list[ProjectFile] = []
    skipped: list[SkippedFile] = []

    for directory, names, filenames in os.walk(resolved_root, followlinks=False):
        directory_path = Path(directory)
        relative_directory = directory_path.relative_to(resolved_root)
        kept_directories: list[str] = []
        for name in sorted(names):
            relative = (relative_directory / name).as_posix()
            path = directory_path / name
            if name in options.excluded_directories:
                continue
            if path.is_symlink():
                continue
            if ignore.match_file(f"{relative}/"):
                continue
            kept_directories.append(name)
        names[:] = kept_directories

        for name in sorted(filenames):
            path = directory_path / name
            relative = path.relative_to(resolved_root).as_posix()
            if path.is_symlink():
                skipped.append(SkippedFile(relative, "symlink"))
                continue
            if ignore.match_file(relative):
                skipped.append(SkippedFile(relative, "ignored"))
                continue
            try:
                size = path.stat().st_size
            except OSError as error:
                skipped.append(SkippedFile(relative, f"unreadable: {error}"))
                continue
            if size > options.max_file_bytes:
                skipped.append(SkippedFile(relative, "size limit"))
                continue
            files.append(ProjectFile(relative, size))
            if len(files) > options.max_files:
                raise InventoryError(
                    f"project contains more than {options.max_files} eligible files"
                )

    return ProjectInventory(resolved_root, tuple(sorted(files)), tuple(sorted(skipped)))
