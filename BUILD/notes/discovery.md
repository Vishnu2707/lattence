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
