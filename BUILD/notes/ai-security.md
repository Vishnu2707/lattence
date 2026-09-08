# AI security module note

T-024 added frozen test case, raw result, and observation result models. The
offline attack runner creates stable tests for attack rules and applicable graph
nodes, evaluates graph field predicates, records both matches and negative
observations, and returns provider-neutral raw results.

Graph predicates support `field` with `equals`, `exists`, or `contains`.
Nested fields use dot-separated dictionary paths.

T-025 added LT-AI-001 for agents without bounded instruction sources and
LT-AI-002 for unclassified retrieved context. Each rule has positive and
negative runner fixtures and AI security mappings.
T-026 added LT-AI-003 for sourced system instructions and LT-AI-004 for
delegated instruction-priority boundaries. Both rules include positive and
negative fixtures.
T-027 added LT-AI-005 for side-effecting output paths and LT-AI-006 for exposed
secret values. Both rules include positive and negative fixtures.
