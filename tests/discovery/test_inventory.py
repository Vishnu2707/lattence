from pathlib import Path

import pytest
from lattence.discovery import (
    InventoryError,
    InventoryOptions,
    SkippedFile,
    inventory_project,
)


def test_inventory_is_sorted_and_applies_default_and_git_ignores(
    tmp_path: Path,
) -> None:
    (tmp_path / ".gitignore").write_text("ignored.txt\ncache/\n", encoding="utf-8")
    (tmp_path / "z.py").write_text("z = 1\n", encoding="utf-8")
    (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("ignored\n", encoding="utf-8")
    (tmp_path / "cache").mkdir()
    (tmp_path / "cache/data.txt").write_text("ignored\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git/config").write_text("ignored\n", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules/module.js").write_text("ignored\n", encoding="utf-8")

    inventory = inventory_project(tmp_path)

    assert [file.path for file in inventory.files] == [".gitignore", "a.py", "z.py"]
    assert inventory.skipped == (SkippedFile("ignored.txt", "ignored"),)


def test_inventory_records_files_over_size_limit(tmp_path: Path) -> None:
    (tmp_path / "small.txt").write_text("small", encoding="utf-8")
    (tmp_path / "large.txt").write_text("x" * 20, encoding="utf-8")

    inventory = inventory_project(
        tmp_path, InventoryOptions(max_file_bytes=10, use_gitignore=False)
    )

    assert [file.path for file in inventory.files] == ["small.txt"]
    assert inventory.skipped[0].path == "large.txt"
    assert inventory.skipped[0].reason == "size limit"


def test_inventory_enforces_file_count(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")

    with pytest.raises(InventoryError, match="more than 1"):
        inventory_project(tmp_path, InventoryOptions(max_files=1, use_gitignore=False))


def test_inventory_rejects_non_directory(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("content", encoding="utf-8")

    with pytest.raises(InventoryError, match="not a directory"):
        inventory_project(target)
