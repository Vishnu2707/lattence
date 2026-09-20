import subprocess
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from .planning import CryptoMutationPlan, UnsafeCryptoMutation


@dataclass(frozen=True)
class CryptoChaosObservation:
    experiment: str
    target_path: str
    executed: bool
    downgrade_accepted: bool | None
    timed_out: bool
    probe_returncode: int | None
    rollback_verified: bool
    original_sha256: str
    mutated_sha256: str | None
    error: str | None = None


def execute_mutation(
    root: Path,
    plan: CryptoMutationPlan,
    *,
    experiment: str,
    probe_command: tuple[str, ...],
) -> CryptoChaosObservation:
    target = root.resolve() / plan.target_path
    original = target.read_bytes()
    original_sha256 = sha256(original).hexdigest()
    if original_sha256 != plan.original_sha256:
        raise UnsafeCryptoMutation("target changed after mutation planning")
    if plan.dry_run:
        return CryptoChaosObservation(
            experiment=experiment,
            target_path=plan.target_path,
            executed=False,
            downgrade_accepted=None,
            timed_out=False,
            probe_returncode=None,
            rollback_verified=True,
            original_sha256=original_sha256,
            mutated_sha256=None,
        )

    content = original.decode("utf-8")
    mutated = content.replace(plan.before_fragment, plan.after_fragment).encode()
    mutated_sha256 = sha256(mutated).hexdigest()
    returncode: int | None = None
    timed_out = False
    error: str | None = None
    try:
        target.write_bytes(mutated)
        try:
            completed = subprocess.run(
                probe_command,
                cwd=root,
                check=False,
                capture_output=True,
                timeout=plan.timeout_seconds,
            )
            returncode = completed.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
        except OSError as exception:
            error = f"probe could not start: {exception.strerror or 'unknown error'}"
    finally:
        target.write_bytes(original)
    rollback_verified = sha256(target.read_bytes()).hexdigest() == original_sha256
    if not rollback_verified:
        raise UnsafeCryptoMutation("failed to restore crypto mutation target")
    return CryptoChaosObservation(
        experiment=experiment,
        target_path=plan.target_path,
        executed=True,
        downgrade_accepted=returncode == 0 if returncode is not None else None,
        timed_out=timed_out,
        probe_returncode=returncode,
        rollback_verified=rollback_verified,
        original_sha256=original_sha256,
        mutated_sha256=mutated_sha256,
        error=error,
    )
