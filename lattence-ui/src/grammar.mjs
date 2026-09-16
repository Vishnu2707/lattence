import { readFileSync } from "node:fs";

const grammarUrl = new URL("./visual-grammar.json", import.meta.url);

export function loadVisualGrammar() {
  return JSON.parse(readFileSync(grammarUrl, "utf8"));
}

export const visualGrammar = Object.freeze(loadVisualGrammar());
