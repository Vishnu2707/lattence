from pathlib import Path

from .execution import CryptoChaosObservation, execute_mutation
from .planning import CryptoMutationPlan, UnsafeCryptoMutation

_CLASSICAL_GROUPS = frozenset({"dhe", "ecdhe", "rsa", "x25519", "x448"})
_PQC_TERMS = ("hybrid", "kyber", "ml-kem")


def execute_key_exchange_downgrade(
    root: Path,
    plan: CryptoMutationPlan,
    *,
    probe_command: tuple[str, ...],
) -> CryptoChaosObservation:
    before = plan.before_fragment.lower()
    after = plan.after_fragment.lower()
    if not any(term in before for term in _PQC_TERMS):
        raise UnsafeCryptoMutation("key-exchange source is not post-quantum or hybrid")
    if after not in _CLASSICAL_GROUPS:
        raise UnsafeCryptoMutation(
            "key-exchange downgrade must select a classical group"
        )
    return execute_mutation(
        root,
        plan,
        experiment="key-exchange-downgrade",
        probe_command=probe_command,
    )
