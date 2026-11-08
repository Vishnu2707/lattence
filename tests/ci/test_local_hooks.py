from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_pre_commit_runs_provenance_and_cached_prose_checks() -> None:
    hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")

    provenance = '"$root/.githooks/check-provenance"'
    prose = '"$root/.githooks/check-prose" --cached'
    assert provenance in hook
    assert prose in hook
    assert hook.index(provenance) < hook.index(prose)


def test_prose_check_supports_the_staged_snapshot() -> None:
    check = (ROOT / ".githooks" / "check-prose").read_text(encoding="utf-8")

    assert '"${1:-}" = "--cached"' in check
    assert "git grep --cached" in check
