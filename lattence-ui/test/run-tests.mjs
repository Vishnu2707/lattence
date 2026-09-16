import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { visualGrammar } from "../src/grammar.mjs";

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

process.stdout.write("visual grammar tests passed\n");
