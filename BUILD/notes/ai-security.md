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
T-028 added LT-AGENT-001 for delegation agency and LT-AGENT-002 for tools with
delete permission. Both rules include positive and negative fixtures.
T-029 added LT-MCP-001 for tools without input schemas and LT-MCP-002 for
credentialed tool servers crossing trust boundaries. Both rules include
positive and negative fixtures.
T-030 added LT-AI-007 for vector-store poisoning paths and LT-AI-008 for
unclassified retrieved context. Both rules include positive and negative
fixtures.
T-031 added LT-AGENT-003 for delegation trust boundaries and LT-AGENT-004 for
persistent memory poisoning. Both rules include positive and negative fixtures.
T-032 added LT-AI-009 for denial and resource exhaustion boundaries. The rule
has positive and negative application fixtures.
