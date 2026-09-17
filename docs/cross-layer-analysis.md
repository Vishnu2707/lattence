# Cross-layer analysis

Cross-layer analysis connects an AI, agent, or MCP finding to a concrete
cryptographic finding. It uses only edges already stored in the security graph.
The workflow does not invent a relationship to complete a chain.

## Generate the presentation

Run the shared workflow against a project checkout:

```bash
lattence tui examples/vulnerable-agent \
  --offline \
  --no-color \
  --out lattence-ui
```

The command renders the terminal view and writes
`lattence-ui/presentation.json`. Add `--json` to write the same document to
standard output. Offline mode keeps optional external engines disabled.

The source project does not need to be imported or executed. Discovery parses
source, configuration, and manifests. The native attack catalog and crypto
assessment produce normalized findings before correlation starts.

## Chain contract

The version 1 presentation document contains the project, security graph,
findings, and `cross_layer_chains`. Every chain identifies:

- the source AI, agent, or MCP finding;
- the destination crypto finding;
- the start and end graph nodes;
- one or more real graph hops;
- a stable explanation; and
- combined finding and edge evidence references.

Every hop records two orientations:

- `source_id` and `target_id` are the stored graph edge direction;
- `from_node_id` and `to_node_id` are the analysis traversal direction; and
- `traversal` is `forward` or `reverse`.

Reverse traversal is necessary when analysis moves from an affected resource
back to the component that accesses or owns it. It does not reverse the stored
edge. The presentation validator rejects missing edges, altered edge types,
invalid orientation, repeated nodes, unknown findings, and chains without a
cryptographic relationship.

Presentation generation searches up to four hops. This bound includes the
accepted two-hop chain while preventing an all-path search from expanding
excessively on a dense graph.

## Accepted example

The vulnerable example contains this real topology:

1. `LT-AI-002` targets `dataset:rag-pipeline:app.py:15`.
2. Analysis traverses the dataset access edge in reverse to
   `tool:app.py:delete_customer_record`.
3. Analysis traverses the tool's `key_exchange` edge forward to the concrete
   X25519 asset.
4. The crypto finding targets that asset and explains the quantum-vulnerable
   endpoint.

The [cross-layer diagram](../assets/diagrams/cross-layer-chain.svg) labels the
stored and traversal direction separately.

## Terminal workflow

The terminal view uses the fixed twelve-section rail. `Attack Graph` lists one
row per cross-layer chain. Opening a row exposes the explanation, each oriented
hop, stored endpoints, traversed endpoints, and evidence references. The
footer documents section, row, detail, hop, help, and quit keys used by the
shared state model. Plain output contains no color escape sequences.

Non-interactive output renders the initial Overview state and remains suitable
for logs and deterministic recordings. The committed
[`tui.gif`](../assets/demo/tui.gif) is generated from the vulnerable example
with no network access.

## Dashboard workflow

The static dashboard reads `presentation.json` from its own directory. After
generating the document, serve that directory with a local static file server:

```bash
python -m http.server --directory lattence-ui 8000
```

The dashboard provides:

- the same twelve-section navigation as the terminal view;
- a dense table with filtering, sortable columns, and virtual row selection;
- vertical-arrow row selection and horizontal-arrow path-hop selection;
- a right-side detail panel instead of a modal;
- local saved-view state; and
- selected JSON copy plus complete presentation export.

The dashboard makes no service request beyond loading the local presentation
document and static files.

## Evidence review

Start with a chain row, then review evidence from the outside in:

1. Confirm that the source finding targets the stated start node.
2. Confirm each `edge_id` exists in `graph.edges` with the recorded stored
   source, target, and type.
3. Follow `from_node_id` to `to_node_id` using the recorded traversal value.
4. Inspect each hop's `evidence_refs` against the scanned checkout.
5. Confirm that the final crypto finding targets the chain endpoint.
6. Review the explanation as a summary, not as a substitute for the edges.

Treat presentation files as sensitive. They contain source paths, node
identifiers, security findings, and evidence references from the scanned
project.
