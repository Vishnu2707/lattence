import re

from lattence.graph import CryptoAlgorithm, Node, SecurityGraph

_POST_QUANTUM = (
    "dilithium",
    "falcon",
    "kyber",
    "ml-dsa",
    "ml-kem",
    "slh-dsa",
    "sphincs",
)
_QUANTUM_VULNERABLE = (
    "diffie-hellman",
    "dsa",
    "ecdh",
    "ecdsa",
    "ed25519",
    "ed448",
    "rsa",
    "x25519",
    "x448",
)
_QUANTUM_SAFE = (
    "aes-256",
    "chacha20",
    "sha-256",
    "sha-384",
    "sha-512",
)


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _contains(value: str, terms: tuple[str, ...]) -> bool:
    return any(term in value for term in terms)


def classify_algorithm(algorithm: CryptoAlgorithm) -> CryptoAlgorithm:
    name = _normalized(algorithm.algorithm)
    post_quantum = _contains(name, _POST_QUANTUM)
    vulnerable = _contains(name, _QUANTUM_VULNERABLE)
    if "hybrid" in name or (post_quantum and vulnerable):
        status = "hybrid"
    elif post_quantum or _contains(name, _QUANTUM_SAFE):
        status = "safe"
    elif vulnerable or name in {"dh", "dhe", "ecdhe"}:
        status = "vulnerable"
    else:
        status = "unknown"
    return algorithm.model_copy(update={"quantum_status": status})


def classify_graph(graph: SecurityGraph) -> SecurityGraph:
    nodes: list[Node] = [
        classify_algorithm(node) if isinstance(node, CryptoAlgorithm) else node
        for node in graph.nodes
    ]
    return graph.model_copy(update={"nodes": nodes})
