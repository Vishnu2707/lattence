# Plugin SDK: writing a SecurityProvider adapter

Lattence normalizes results from external security engines through one
frozen interface, `SecurityProvider`, defined in `BUILD/CONTRACTS.md` and
implemented at `lattence-cli/src/lattence/providers/runtime.py`. This
document explains how to write an adapter against that interface, using the
three shipped adapters, Garak, PyRIT, and Promptfoo, as worked reference
implementations at `lattence-cli/src/lattence/providers/{garak,pyrit,
promptfoo}.py`.

## The interface

```python
class SecurityProvider(Protocol):
    def discover(self, project: Project) -> list[Node]: ...
    def generate_tests(self, graph: SecurityGraph) -> list[TestCase]: ...
    def execute(self, test: TestCase) -> RawResult: ...
    def normalize_results(self, raw: RawResult) -> list[Finding]: ...
```

`SecurityProvider` is a `typing.Protocol`, checked with
`@runtime_checkable`. An adapter is any class that implements these four
methods with these signatures. It does not need to inherit from anything.
`validate_provider` in `runtime.py` checks that all four methods exist and
are callable before a provider is used; it does not check behavior.

### `discover(project) -> list[Node]`

Return additional graph nodes your engine can identify from the `Project`
that Lattence's own discovery did not already find, or an empty list. All
three reference adapters return `[]`: they rely entirely on the graph
Lattence has already built. `run_external_providers` in
`lattence.cli.workflow` rejects a provider that discovers a node with an id
that already exists in the graph.

### `generate_tests(graph) -> list[TestCase]`

Inspect the `SecurityGraph` and return one `TestCase` per node you intend to
test. `TestCase.target_node_id` must name a node that exists in the graph;
`run_external_providers` rejects a test that targets an unknown node id. See
`GarakProvider.generate_tests`, which emits one test per `model` node, using
`node.endpoint` or `node.provider` and `node.model_name` to build the
engine-specific target configuration in `TestCase.inputs`.

### `execute(test) -> RawResult`

Run your engine against one `TestCase` and return a `RawResult`. This is the
only method that performs I/O, an external process, subprocess call, or
HTTP request. `GarakProvider.execute` shells out to the `garak` CLI with a
`subprocess.run`-based executor that is injectable at construction time
(`GarakProvider(executor=..., work_directory=...)`), which is what makes the
adapter testable without the real binary installed. `RawResult.payload` is
free-form `JsonValue`; put whatever your engine returned there, in a shape
`normalize_results` can parse back out. Put the raw engine failure, if any,
in `RawResult.error` rather than raising, so a single failed test does not
abort the whole provider run.

### `normalize_results(raw) -> list[Finding]`

Parse `RawResult.payload` back into zero or more `Finding` values. This is
where your engine's result format becomes Lattence's frozen `Finding`
schema. Providers do not decide severity, status, or policy outcome as a
policy matter; they only classify what actually happened. Follow
`GarakProvider._normalize_record` as the pattern:

- Build a deterministic finding id from a hash of stable inputs (target node,
  probe, detector), not from a counter, so repeated runs against the same
  target produce the same id.
- Build a complete `EvidenceBundle`: at least one `EvidenceInput` with a
  `sha256` of the serialized evidence value, `started_at`/`finished_at` from
  the `RawResult`, an `EnvironmentFingerprint`, and a `PolicyDecision` with
  `outcome="skip"` and a reason noting that central policy evaluation has
  not run yet, since a provider adapter does not decide policy outcomes.
- Build a `ReproductionRecipe` with the actual command or call used, so
  `verify` and `harden` have something to act on later.
- Return `[]` rather than raising when a raw result cannot be parsed. A
  malformed or empty engine result is not a Lattence-level failure.

## Wiring a provider into the CLI

An adapter that only implements `SecurityProvider` works with
`run_external_providers` directly, but `provider enable NAME` and the
`enabled_providers()` factory that `attack` calls when not `--offline` use a
fixed name-to-adapter mapping in
`lattence-cli/src/lattence/providers/registry.py` (`_EXECUTABLES` and the
`factories` dict inside `enabled_providers`). There is no dynamic plugin
discovery today: adding a fourth built-in provider means extending that
mapping in the same way Garak, PyRIT, and Promptfoo are registered, in a
task that touches `registry.py`. A third party integrating a private or
in-house engine can still use their `SecurityProvider` implementation
directly with `run_external_providers(report, [MyProvider()])` without going
through the CLI's `provider enable` flow at all.

## Testing an adapter

Reference the adapter test suites at
`tests/cli/providers/test_garak.py`, `test_pyrit.py`, and
`test_promptfoo.py`. They inject a fake executor to avoid depending on the
real external binary, assert `generate_tests` only targets nodes that exist
in a fixture graph, and assert `normalize_results` on both a matching and a
non-matching raw payload.
