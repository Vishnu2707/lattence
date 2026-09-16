# Frozen contracts

Version: 1.0. These contracts are frozen for v0.1. A change requires a decision
record, a migration note, and an explicit contract task.

## Shared types

- `JsonValue`: null, bool, int, float, str, list of `JsonValue`, or a string-keyed
  mapping of `JsonValue`.
- `NodeId`: stable string formed as `<type>:<project-relative-identity>`.
- `SourceRef`: `path: str`, `line: int | None`, `column: int | None`,
  `symbol: str | None`.
- All models use Pydantic v2 with `extra="forbid"` and frozen instances at
  contract boundaries.
- All timestamps are timezone-aware UTC values serialized as RFC 3339 strings.
- Paths in persisted output are project-relative POSIX paths.

## Project model

`Project` fields: `id: str`, `name: str`, `root: str`, `version: str = "1"`,
`scanned_at: datetime`, `source_revision: str | None = None`,
`nodes: list[Node] = []`, `metadata: dict[str, JsonValue] = {}`.

Every node carries `id: NodeId`, `type: NodeType`, `name: str`,
`source: SourceRef | None`, `tags: set[str] = set()`, and
`metadata: dict[str, JsonValue] = {}`. Each concrete node contains those fields
plus the fields below.

- `Application`: `frameworks: list[str] = []`, `entrypoints: list[str] = []`,
  `runtime: str | None`, `deployment: str | None`.
- `Agent`: `framework: str | None`, `instructions_source: SourceRef | None`,
  `model_ids: list[NodeId] = []`, `tool_ids: list[NodeId] = []`,
  `memory_enabled: bool = False`, `delegation_enabled: bool = False`.
- `Model`: `provider: str`, `model_name: str`, `endpoint: str | None`,
  `local: bool = False`, `capabilities: set[str] = set()`.
- `Tool`: `description: str | None`, `input_schema: dict[str, JsonValue] = {}`,
  `side_effects: bool = False`, `permissions: set[str] = set()`,
  `server_id: NodeId | None`.
- `MCPServer`: `transport: str`, `command: str | None`, `url: str | None`,
  `auth_method: str | None`, `tool_ids: list[NodeId] = []`.
- `API`: `base_url: str | None`, `protocol: str`, `auth_method: str | None`,
  `operations: list[str] = []`, `external: bool = False`.
- `Database`: `engine: str`, `host: str | None`, `database: str | None`,
  `encrypted: bool | None`, `credential_id: NodeId | None`.
- `Secret`: `kind: str`, `location: str`, `exposed_value: bool = False`,
  `environment_name: str | None`; secret values are never stored.
- `Identity`: `kind: str`, `principal: str | None`, `provider: str | None`,
  `scopes: set[str] = set()`, `privileged: bool = False`.
- `Certificate`: `subject: str | None`, `issuer: str | None`,
  `serial_number: str | None`, `not_before: datetime | None`,
  `not_after: datetime | None`, `signature_algorithm: str | None`,
  `public_key_algorithm: str | None`, `public_key_bits: int | None`,
  `file_path: str | None`.
- `CryptoAlgorithm`: `algorithm: str`, `purpose: str`,
  `key_size_bits: int | None`, `quantum_status: Literal["safe", "hybrid",
  "vulnerable", "unknown"]`, `implementation: str | None`.
- `ExternalService`: `service_type: str`, `host: str | None`,
  `provider: str | None`, `auth_method: str | None`, `data_classes: set[str] = set()`.
- `Dataset`: `format: str | None`, `location: str | None`,
  `sensitivity: Literal["public", "internal", "confidential", "restricted",
  "unknown"] = "unknown"`, `vectorized: bool = False`.

`Node` is the discriminated union of all concrete nodes, using `type` as the
discriminator. `NodeType` is the snake-case form of each concrete class name.

## Graph schema

The graph is a directed multigraph. Nodes are the project model nodes. Parallel
edges are allowed when distinct evidence supports the same relationship.

`Edge` fields: `id: str`, `source_id: NodeId`, `target_id: NodeId`,
`type: EdgeType`, `permission: str | None`, `auth_method: str | None`,
`transport: str | None`, `algorithm: str | None`,
`trust_level: Literal["untrusted", "low", "medium", "high", "system",
"unknown"] = "unknown"`, `evidence_refs: list[str] = []`,
`metadata: dict[str, JsonValue] = {}`.

`EdgeType` values: `calls`, `accesses`, `trusts`, `authenticated_by`,
`protected_by`, `key_exchange`, `contains`, `delegates_to`.

`SecurityGraph` fields: `version: Literal["1"]`, `project_id: str`,
`nodes: list[Node]`, `edges: list[Edge]`, `generated_at: datetime`.

## Finding schema

Finding identifiers match `^LT-[A-Z][A-Z0-9]*-[0-9]{3}$`. Domains include
`AI`, `AGENT`, `MCP`, `CRYPTO`, `PQC`, and `POLICY`.

`Finding` fields: `id: str`, `title: str`, `source: str`,
`severity: Literal["critical", "high", "medium", "low", "info"]`,
`confidence: Literal["high", "medium", "low"]`,
`owasp_llm: list[str] = []`, `owasp_agentic: list[str] = []`,
`cwe: list[str] = []`, `target_node_id: NodeId`,
`evidence: EvidenceBundle`, `reproduction: ReproductionRecipe`,
`remediation: str`, `status: Literal["open", "accepted", "fixed",
"false_positive"] = "open"`.

## Evidence bundle

`EvidenceBundle` fields: `id: str`, `inputs: list[EvidenceInput]`,
`transcript: list[TranscriptEntry]`, `telemetry_spans: list[TelemetrySpan]`,
`policy_decision: PolicyDecision`, `started_at: datetime`,
`finished_at: datetime`, `environment: EnvironmentFingerprint`,
`replay_seed: int`.

Supporting models:

- `EvidenceInput`: `name: str`, `media_type: str`, `sha256: str`,
  `value: JsonValue | None`; sensitive values use null.
- `TranscriptEntry`: `sequence: int`, `actor: str`, `kind: str`,
  `content: JsonValue`, `timestamp: datetime`.
- `TelemetrySpan`: `trace_id: str`, `span_id: str`, `parent_span_id: str | None`,
  `name: str`, `start_time: datetime`, `end_time: datetime`,
  `attributes: dict[str, JsonValue] = {}`.
- `PolicyDecision`: `policy_id: str`, `outcome: Literal["pass", "fail",
  "warn", "skip", "blocked"]`, `reason: str`, `facts: dict[str, JsonValue] = {}`.
- `EnvironmentFingerprint`: `platform: str`, `python: str`,
  `lattence_version: str`, `project_revision: str | None`,
  `dependency_digest: str`, `configuration_digest: str`.
- `ReproductionRecipe`: `command: list[str]`, `working_directory: str`,
  `environment_names: list[str] = []`, `expected: str`, `offline: bool = True`.

## Plugin interface

```python
class SecurityProvider:
    def discover(self, project: Project) -> list[Node]: ...
    def generate_tests(self, graph: SecurityGraph) -> list[TestCase]: ...
    def execute(self, test: TestCase) -> RawResult: ...
    def normalize_results(self, raw: RawResult) -> list[Finding]: ...
```

`TestCase` fields: `id: str`, `title: str`, `target_node_id: NodeId`,
`inputs: dict[str, JsonValue]`, `timeout_seconds: float`, `replay_seed: int`.
`RawResult` fields: `provider: str`, `test_id: str`, `started_at: datetime`,
`finished_at: datetime`, `payload: JsonValue`, `error: str | None`.

Providers do not decide severity, status, or policy outcome. Normalized findings
are validated and passed to the policy engine.

## CLI contract

Commands: `scan [PATH]`, `attack [PATH]`, `harden [PATH]`, `verify FINDING_ID`,
`report [INPUT]`, `tui [INPUT]`, `pqc assess [PATH]`,
`crypto chaos [PATH]`, `provider enable NAME`, `provider list`,
`graph export [INPUT]`, and `policy check [INPUT]`.

Every command accepts `--json`, `--out PATH`, `--offline`, `--no-color`,
`--quiet`, `--planner [rules|llm]`, and
`--fail-on [critical|high|medium|low|info|none]`. Defaults are plain terminal
output, current directory output, online permitted, color when supported,
normal logging, rules planner, and `high` failure threshold.

Machine output goes to stdout. Logs go to stderr. Exit codes are 0 for clean,
1 for findings at or above the gate, 2 for usage errors, and 3 for internal
errors. Non-interactive output contains no terminal escape sequences.
`attack` requires `lattence.targets.yaml` and refuses execution without it.

## Rule pack format

Rule packs are YAML documents validated by `docs/schemas/rule-pack.v1.json`.
Each document has `version`, `id`, `kind`, `title`, `description`, `severity`,
`confidence`, `applies_to`, `match`, `finding`, and optional `tests` fields.
Rules use declarative path, dependency, syntax, configuration, and graph
predicates. A new deterministic detection or attack belongs in YAML when the
schema can express it.

## Report schema

JSON reports validate against `docs/schemas/report.v1.json`. The top-level
fields are `schema_version`, `tool`, `project`, `graph`, `findings`,
`generated_at`, and `summary`. Writers emit stable key order. Unknown fields
are rejected. Report schema version changes require a migration note.

The version 1 summary may include `quantum_vulnerable_assets` and
`quantum_vulnerable_paths`, both non-negative integers defaulting to zero when
absent. A quantum-vulnerable asset is isolated only when it has no incoming
relationship in the crypto dependency projection. A quantum-vulnerable path
contains at least two nodes and at least one relationship, ends at a
quantum-vulnerable crypto asset, and preserves its ordered relationship and
source evidence. A one-node, zero-relationship record is never a path.

Migration note: v0.4.1 adds the two optional summary fields without changing
`schema_version`. Reports written before v0.4.1 remain valid and deserialize
both counts as zero. v0.4.1 writers emit both fields. Consumers must not derive
path counts from isolated asset counts or from the number of vulnerable nodes.
