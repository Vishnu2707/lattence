"""Validate the release archives and compare clean-wheel command help."""

import argparse
import subprocess
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path

COMMANDS = (
    (),
    ("scan",),
    ("attack",),
    ("harden",),
    ("verify",),
    ("report",),
    ("tui",),
    ("pqc", "assess"),
    ("crypto", "chaos"),
    ("provider", "enable"),
    ("provider", "list"),
    ("graph", "export"),
    ("graph", "chain"),
    ("policy", "check"),
)


def check_archives(wheel: Path, source: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        )
        metadata = Parser().parsestr(archive.read(metadata_name).decode())
        names = set(archive.namelist())
        assert metadata["Name"] == "lattence"
        assert metadata["Version"] == "1.0.0"
        assert metadata["License-Expression"] == "Apache-2.0"
        assert metadata["Description-Content-Type"] == "text/markdown"
        assert "Lattence scans an agentic codebase" in metadata.get_payload()
        assert any(name.endswith(".dist-info/licenses/LICENSE") for name in names)
        assert "lattence/packs/attacks/native.yaml" in names or any(
            name.startswith("lattence/packs/attacks/") for name in names
        )
        assert "lattence/assets/banner.txt" in names
        assert "lattence/schemas/report.v1.json" in names
        print(f"WHEEL  {wheel.name}  metadata and bundled assets PASS")

    with tarfile.open(source, "r:gz") as archive:
        names = set(archive.getnames())
        assert any(name.endswith("/README.md") for name in names)
        assert any(name.endswith("/LICENSE") for name in names)
        assert any(name.endswith("/pyproject.toml") for name in names)
        print(f"SDIST  {source.name}  README and license PASS")


def _output(binary: Path, *arguments: str) -> str:
    result = subprocess.run(
        [str(binary), *arguments],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def check_commands(source_binary: Path, wheel_binary: Path) -> None:
    assert _output(source_binary, "--version") == _output(wheel_binary, "--version")
    print("VERSION  source and clean wheel match")
    for command in COMMANDS:
        arguments = (*command, "--help")
        assert _output(source_binary, *arguments) == _output(
            wheel_binary, *arguments
        ), " ".join(arguments)
    print(f"HELP  root and {len(COMMANDS) - 1} commands match")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("source_binary", type=Path)
    parser.add_argument("wheel_binary", type=Path)
    options = parser.parse_args()
    check_archives(options.wheel, options.source)
    check_commands(options.source_binary, options.wheel_binary)


if __name__ == "__main__":
    main()
