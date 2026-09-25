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
T-033 added a strict catalog loader. The native catalog contains exactly 15
unique, sorted attack rules and rejects incomplete or non-attack collections.

T-047 added `AttackRunner.replay(rule_id, target_node_id)` and
`verify_finding(report, finding_id, rules)`. Replay rebuilds the same
`TestCase` `observe` already builds internally (same id, seed, and inputs
shape), so it is not new detection logic, just a public single-test entry
point that does not require regenerating every test for every node.
`verify_finding` looks up a `Finding` by id in an existing `Report`, replays
it against that report's own embedded `SecurityGraph`, and returns
`VULNERABLE` (still matches), `RESOLVED` (no longer matches), or
`NOT_FOUND` (unknown finding id, rule, or target node). It takes no project
path and does not rescan: verification is a property of the report you
already have, not a fresh scan. This is what T-048's `verify` command
wires up.

T-092 correlates AI, agent, and MCP findings with PQC and crypto findings over
the bounded topology traversal. A correlation requires a genuine
`key_exchange` or `protected_by` edge, retains every hop and its orientation,
and combines both finding evidence identifiers with graph evidence paths.
Unknown finding targets fail explicitly, and unrelated finding domains or
paths without a cryptographic relationship produce no correlation.

T-105 calls the correlator directly with the report and crypto findings built
from discovering `examples/vulnerable-agent`. It verifies the real two-hop
`LT-AI-002` to `LT-PQC-203` route, both stored edges, both traversal
directions, the evidence paths, and all seven crypto algorithm relationships
owned by the connected tool.

T-156 audited all 15 native attack rules and all 23 native detection rules
for matching on node field shape without checking a real data-flow path
(the bug class found live at workflow.py:208). Added
`MatchSpec.requires_path` (`lattence-core/src/lattence/discovery/models.py`,
schema in `rule-pack.v1.json`) and wired it into `AttackRunner.observe`
(`lattence-ai/src/lattence_ai/attacks/runner.py`), which calls the existing
`lattence.graph.traversal.find_attack_paths` only after the node's own
field predicate already matched. Applied to LT-AI-002, LT-AI-007, and
LT-AI-008, the three rules whose finding text makes a reachability claim.
Added `tests/ai/attacks/test_dataflow_precision.py` as the distinct
regression module, and updated the existing positive fixtures in
`test_prompt_injection.py` and `test_retrieval.py` to include a real
agent-to-sink path, since an isolated node is no longer a valid "should
match" fixture for these three rules. Full audit table is in
`BUILD/DECISIONS.md` (D-032). Methodology written up in
`docs/false-positive-methodology.md`.
