# False positive methodology

This document describes how Lattence tracks false positive precision in its
native rule packs release over release, and the specific bug class fixed in
the detection precision hardening milestone.

## The bug class: shape without flow

A native attack rule (`kind: attack` in `lattence-packs/attacks`) matches
against the security graph built from a scanned project. Most rules assert
an intrinsic property of one node, such as "this tool has delete
permission" or "this agent has no bounded instruction source." Those claims
are true or false about the node alone, and a single-node field predicate is
the right check for them.

A smaller set of rules instead make a reachability claim in their finding
text: that untrusted or unclassified content actually reaches an agent.
Checking only the node's own fields for that class of rule answers the
wrong question. A node can carry the matching field shape, such as
`sensitivity: unknown` on a `dataset` node, purely as a side effect of how
the discovery layer classified some unrelated source text, without any
agent, tool, or pipeline ever consuming it.

This is exactly what happened at
`lattence-cli/src/lattence/cli/workflow.py:208`: an f-string building an
error message, `f"provider test targets unknown node: {test.target_node_id}"`,
was discovered as a `dataset` node named after a chroma collection, with the
default `sensitivity: unknown`. Rules LT-AI-002 and LT-AI-008 both fired on
it, reporting indirect prompt injection and untrusted retrieved context
against a line of error-handling code that no agent ever reached.

## The fix

Rules whose finding text makes a reachability claim now declare
`match.requires_path` in their rule pack YAML:

```yaml
match:
  graph:
    field: sensitivity
    equals: unknown
  requires_path:
    from_type: agent
    edge_types: [calls, accesses]
    max_depth: 4
```

`AttackRunner` (`lattence-ai/src/lattence_ai/attacks/runner.py`) evaluates
the existing single-node `graph` predicate first, and only when that
predicate matches does it call `lattence.graph.traversal.find_attack_paths`,
the same bounded-depth graph traversal the CLI's `graph chain` command and
the cross-layer correlator already use, to look for a real edge path from
any node of `from_type` to the candidate node. The rule only fires when
both the shape and the path are present. No second traversal mechanism was
built; this reuses the one the security graph already has.

Fixed in this pass: LT-AI-002 (indirect prompt injection), LT-AI-007
(retrieval corpus poisoning), LT-AI-008 (untrusted retrieved context). The
full audit of all 15 native attack rules and all 23 native detection rules,
with the reasoning for each, is in `BUILD/DECISIONS.md` under "Milestone A
audit: native rule taint/data-flow soundness."

## Regression coverage

`tests/ai/attacks/test_dataflow_precision.py` is a distinct, trackable test
module for this bug class. Each fixed rule gets two fixtures: one where a
real agent-to-sink path exists and the rule should fire, and one styled
directly on the workflow.py case, a node with the identical matching field
shape but no path to any agent, which should not fire. The existing
per-rule test modules (`test_prompt_injection.py`, `test_retrieval.py`) were
also updated so their positive fixtures include a real path, since an
isolated node is no longer a valid "should match" fixture for these three
rules.

## Tracking the rate release over release

Each release records, in `BUILD/STATE.md`, the literal self-scan finding
count from `lattence scan .` run against this repository's own tree, split
by rule id and target node, immediately before and after a precision fix
lands. A fix is only credited if:

- the specific false-positive target node not longer appears for the fixed
  rule id, and
- the deliberately vulnerable fixtures in `examples/vulnerable-agent` still
  produce a finding for every rule they are designed to trigger.

Milestone A's before/after numbers: self-scan against this repository
found 13 findings before the fix and 13 after. The count is unchanged
because the same real RAG dataset in `examples/vulnerable-agent/app.py`
that should have been flagged was, before the fix, masked by the
`workflow.py:208` false positive colliding with it on the same rule ids.
After the fix, LT-AI-002 and LT-AI-008 report the genuine
`dataset:rag-pipeline:examples/vulnerable-agent/app.py:15` node instead of
the spurious `dataset:chroma:lattence-cli/src/lattence/cli/workflow.py:208`
node, so the fix corrected one false positive and one false negative at
once, on rules that were colliding on the same wrong target.
