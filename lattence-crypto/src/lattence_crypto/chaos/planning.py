from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath

MAX_TARGET_BYTES = 1_048_576
MAX_REPLACEMENTS = 32


class UnsafeCryptoMutation(ValueError):
    pass


@dataclass(frozen=True)
class CryptoMutationPlan:
    target_path: str
    original_sha256: str
    before_fragment: str
    after_fragment: str
    replacements: int
    timeout_seconds: float
    dry_run: bool


def _relative_target(root: Path, target_path: str) -> tuple[Path, str]:
    requested = PurePosixPath(target_path)
    if requested.is_absolute() or ".." in requested.parts:
        raise UnsafeCryptoMutation("target must be a project-relative path")
    resolved_root = root.resolve()
    resolved_target = (resolved_root / Path(*requested.parts)).resolve()
    try:
        relative = resolved_target.relative_to(resolved_root).as_posix()
    except ValueError as error:
        raise UnsafeCryptoMutation("target resolves outside the project") from error
    return resolved_target, relative


def plan_crypto_mutation(
    root: Path,
    target_path: str,
    *,
    declared_paths: tuple[str, ...],
    before_fragment: str,
    after_fragment: str,
    timeout_seconds: float = 5.0,
    dry_run: bool = True,
) -> CryptoMutationPlan:
    """Validate and describe one bounded mutation without changing the target."""
    target, relative = _relative_target(root, target_path)
    declarations = {PurePosixPath(path).as_posix() for path in declared_paths}
    if relative not in declarations:
        raise UnsafeCryptoMutation(f"target is not declared: {relative}")
    if timeout_seconds <= 0 or timeout_seconds > 60:
        raise UnsafeCryptoMutation(
            "timeout must be greater than 0 and at most 60 seconds"
        )
    if not before_fragment or before_fragment == after_fragment:
        raise UnsafeCryptoMutation("mutation fragments must be non-empty and different")
    try:
        data = target.read_bytes()
    except OSError as error:
        raise UnsafeCryptoMutation(
            f"cannot read declared target: {relative}"
        ) from error
    if len(data) > MAX_TARGET_BYTES:
        raise UnsafeCryptoMutation("target exceeds the one-megabyte mutation limit")
    try:
        content = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise UnsafeCryptoMutation("target must be UTF-8 text") from error
    replacements = content.count(before_fragment)
    if replacements == 0:
        raise UnsafeCryptoMutation("source fragment was not found in target")
    if replacements > MAX_REPLACEMENTS:
        raise UnsafeCryptoMutation("mutation exceeds the 32-replacement limit")
    return CryptoMutationPlan(
        target_path=relative,
        original_sha256=sha256(data).hexdigest(),
        before_fragment=before_fragment,
        after_fragment=after_fragment,
        replacements=replacements,
        timeout_seconds=timeout_seconds,
        dry_run=dry_run,
    )
