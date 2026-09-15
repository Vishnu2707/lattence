from pathlib import Path

from .execution import CryptoChaosObservation, execute_mutation
from .planning import CryptoMutationPlan, UnsafeCryptoMutation

_CLASSICAL_SIGNATURES = frozenset({"dsa", "ecdsa", "ed25519", "ed448", "rsa"})
_PQC_TERMS = ("dilithium", "falcon", "hybrid", "ml-dsa", "slh-dsa", "sphincs")


def execute_signature_downgrade(
    root: Path,
    plan: CryptoMutationPlan,
    *,
    probe_command: tuple[str, ...],
) -> CryptoChaosObservation:
    before = plan.before_fragment.lower()
    after = plan.after_fragment.lower()
    if not any(term in before for term in _PQC_TERMS):
        raise UnsafeCryptoMutation("signature source is not post-quantum or hybrid")
    if after not in _CLASSICAL_SIGNATURES:
        raise UnsafeCryptoMutation(
            "signature downgrade must select a classical algorithm"
        )
    return execute_mutation(
        root,
        plan,
        experiment="signature-downgrade",
        probe_command=probe_command,
    )
