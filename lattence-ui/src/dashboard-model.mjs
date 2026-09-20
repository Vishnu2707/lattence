export function rowsForSection(presentation, section) {
  if (section === "Attack Graph") {
    return presentation.cross_layer_chains ?? [];
  }
  if (["Findings", "AI Security", "Agent Security", "MCP"].includes(section)) {
    const prefix = {
      "AI Security": "LT-AI-",
      "Agent Security": "LT-AGENT-",
      MCP: "LT-MCP-",
    }[section];
    return (presentation.findings ?? []).filter(
      (finding) => prefix === undefined || finding.id.startsWith(prefix),
    );
  }
  const type = {
    Applications: "application",
    Cryptography: "crypto_algorithm",
  }[section];
  return (presentation.graph?.nodes ?? []).filter(
    (node) => type === undefined || node.type === type,
  );
}

export function filterRows(rows, query) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) return [...rows];
  return rows.filter((row) => JSON.stringify(row).toLowerCase().includes(normalized));
}

export function sortRows(rows, field, direction = "ascending") {
  const multiplier = direction === "descending" ? -1 : 1;
  return [...rows].sort((left, right) => {
    const a = String(left[field] ?? "");
    const b = String(right[field] ?? "");
    return a.localeCompare(b) * multiplier;
  });
}

export function moveSelection(index, movement, rowCount) {
  if (!rowCount) return 0;
  return (index + movement + rowCount) % rowCount;
}

export function hopRows(chain) {
  return (chain?.hops ?? []).map((hop) => ({
    id: hop.edge_id,
    relationship: hop.edge_type,
    traversal: hop.traversal,
    path: `${hop.from_node_id} -> ${hop.to_node_id}`,
    evidence: hop.evidence_refs ?? [],
  }));
}

export function visibleRows(rows, scrollTop, viewportHeight, rowHeight = 32) {
  const start = Math.max(0, Math.floor(scrollTop / rowHeight) - 2);
  const count = Math.ceil(viewportHeight / rowHeight) + 4;
  return { start, rows: rows.slice(start, start + count), total: rows.length };
}
