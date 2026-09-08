# Discovery module

The discovery module currently loads deterministic YAML rule packs. It validates
each document against the bundled v1 JSON Schema, then creates frozen Pydantic
models. Directory loading is filename-sorted and rejects duplicate finding ids.
The bundled schema is tested byte-for-structure against the documented schema.
Project inventory walks files in stable path order, applies root ignore rules,
does not follow symlinks, excludes dependency and build directories, and records
files skipped by ignore or size limits. File count and byte limits are explicit.

Public imports come from `lattence.discovery`. They include `RulePack`,
`MatchSpec`, `FindingTemplate`, `RuleTest`, `RulePackError`, `load_rule_pack`,
and `load_rule_packs`.
Inventory imports are `InventoryOptions`, `ProjectFile`, `SkippedFile`,
`ProjectInventory`, `InventoryError`, and `inventory_project`.
Python syntax parsing uses the standard AST without executing source. It records
imports, call names, decorator names, assignment shapes, and source locations.
Literal values are replaced with type markers. Public imports include
`parse_python_source`, `parse_python_file`, `PythonSyntax`, and their record and
error types.
JavaScript and TypeScript syntax parsing masks comments and literal content,
then records static module imports, CommonJS module loads, qualified call names,
and source locations. It never executes source. Public imports include
`parse_javascript_source`, `parse_javascript_file`, `JavaScriptSyntax`, and
their record and error types.
Dependency discovery reads standard Python project files, requirements files,
and Node package manifests. It records ecosystem, name, specifier, dependency
group, source path, and source line where available. It never installs or
resolves packages. Public imports include `discover_dependency_manifests`,
`DependencyInventory`, `Dependency`, and `DependencyManifestError`.
Framework detection applies YAML rules to dependency, import, and call records.
It emits stable application and agent nodes with source evidence and no literal
configuration values. Six v0.1 framework families are covered. The public entry
point is `detect_frameworks`.
Provider detection applies YAML rules to dependency, import, and call records.
It emits model nodes with stable ids, source evidence, provider identity, local
status, and whether a model keyword was configured. Literal model values and
credentials are never retained. The public entry point is `detect_models`.
Agent and tool detection recognizes agent constructors, tool decorators, and
tool registration calls. It infers read, write, delete, and execute permissions
from declared names, marks side effects, and links same-file tools and models to
agents. Delegation and memory calls set explicit agent flags. Public imports are
`detect_agents_and_tools` and `AgentToolDiscovery`.
Data path detection applies YAML rules to dependency, import, and call records.
It emits vector database nodes and source-located dataset nodes for retrieval,
embedding, indexing, and query operations. It covers four vector stores and a
generic RAG pipeline. The public entry point is `detect_data_paths`.
Service detection applies YAML rules to dependency, import, and call records.
It emits API, database, cache, and source-located external service nodes without
retaining destination values. It covers three web service families, PostgreSQL,
Redis, and common HTTP clients. The public entry point is `detect_services`.
Credential discovery records environment and assignment names that indicate
secrets, but never stores their values. It also identifies OAuth and JWT usage
from imports and calls, then emits source-located identity nodes. Public imports
are `detect_identities` and `IdentityDiscovery`.
Infrastructure discovery identifies container build and composition files,
cluster workload manifests, infrastructure definitions, and CI workflows. It
emits source-located application and external service nodes. The public entry
point is `discover_infrastructure`.
