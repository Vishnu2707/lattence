# Discovery module

The discovery module currently loads deterministic YAML rule packs. It validates
each document against the bundled v1 JSON Schema, then creates frozen Pydantic
models. Directory loading is filename-sorted and rejects duplicate finding ids.
The bundled schema is tested byte-for-structure against the documented schema.

Public imports come from `lattence.discovery`. They include `RulePack`,
`MatchSpec`, `FindingTemplate`, `RuleTest`, `RulePackError`, `load_rule_pack`,
and `load_rule_packs`.
