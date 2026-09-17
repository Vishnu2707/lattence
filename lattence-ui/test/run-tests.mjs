import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { visualGrammar } from "../src/grammar.mjs";
import {
  filterRows,
  hopRows,
  moveSelection,
  rowsForSection,
  sortRows,
  visibleRows,
} from "../src/dashboard-model.mjs";

const expectedNavigation = [
  "Overview",
  "Applications",
  "Attack Surface",
  "AI Security",
  "Agent Security",
  "MCP",
  "Cryptography",
  "PQC Readiness",
  "Attack Graph",
  "Findings",
  "Verification",
  "Reports",
];

assert.equal(visualGrammar.version, "1");
assert.deepEqual(visualGrammar.navigation, expectedNavigation);
assert.equal(visualGrammar.geometry.rowHeight, 32);
assert.equal(visualGrammar.detail.placement, "right-side-panel");
assert.equal(visualGrammar.detail.modal, false);
assert.equal(visualGrammar.table.keyboardNavigation, true);

const css = readFileSync(new URL("../src/tokens.css", import.meta.url), "utf8");
for (const value of Object.values(visualGrammar.colors)) {
  assert.ok(css.includes(value), `missing color token ${value}`);
}

const presentation = {
  graph: { nodes: [{ id: "application:z", type: "application" }] },
  findings: [
    { id: "LT-AI-002", severity: "high" },
    { id: "LT-PQC-203", severity: "medium" },
  ],
  cross_layer_chains: [
    {
      id: "cross-layer:one",
      hops: [
        {
          edge_id: "edge:one",
          edge_type: "reads_from",
          traversal: "reverse",
          from_node_id: "dataset:rag",
          to_node_id: "tool:retrieval",
          evidence_refs: ["app.py:15"],
        },
      ],
    },
  ],
};
assert.equal(rowsForSection(presentation, "Applications").length, 1);
assert.equal(rowsForSection(presentation, "AI Security").length, 1);
assert.equal(rowsForSection(presentation, "Attack Graph").length, 1);
assert.equal(filterRows(presentation.findings, "pqc").length, 1);
assert.equal(sortRows(presentation.findings, "id")[0].id, "LT-AI-002");
assert.equal(moveSelection(0, -1, 2), 1);
assert.deepEqual(hopRows(presentation.cross_layer_chains[0])[0], {
  id: "edge:one",
  relationship: "reads_from",
  traversal: "reverse",
  path: "dataset:rag -> tool:retrieval",
  evidence: ["app.py:15"],
});
assert.deepEqual(visibleRows([1, 2, 3, 4], 32, 32), {
  start: 0,
  rows: [1, 2, 3, 4],
  total: 4,
});

process.stdout.write("visual grammar tests passed\n");
