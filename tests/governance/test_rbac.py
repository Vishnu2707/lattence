from pathlib import Path

from lattence.governance import ApiKeyStore, Role


def test_create_key_resolves_to_caller_and_roles(tmp_path: Path) -> None:
    store = ApiKeyStore(tmp_path / "governance.db")

    key = store.create_key("alice", frozenset({Role.READ_FINDINGS, Role.RUN_SCANS}))
    identity = store.resolve(key)

    assert identity is not None
    assert identity.caller_id == "alice"
    assert identity.roles == frozenset({Role.READ_FINDINGS, Role.RUN_SCANS})


def test_resolve_unknown_key_returns_none(tmp_path: Path) -> None:
    store = ApiKeyStore(tmp_path / "governance.db")

    assert store.resolve("not-a-real-key") is None


def test_list_keys_and_revoke(tmp_path: Path) -> None:
    store = ApiKeyStore(tmp_path / "governance.db")
    store.create_key("alice", frozenset({Role.READ_FINDINGS}))
    store.create_key("bob", frozenset({Role.RUN_ATTACKS}))

    records = store.list_keys()
    assert {record.caller_id for record in records} == {"alice", "bob"}

    removed = store.revoke_caller("alice")
    assert removed == 1
    assert {record.caller_id for record in store.list_keys()} == {"bob"}


def test_store_persists_across_instances(tmp_path: Path) -> None:
    db_path = tmp_path / "governance.db"
    key = ApiKeyStore(db_path).create_key("alice", frozenset({Role.MANAGE_POLICY}))

    reopened = ApiKeyStore(db_path)
    identity = reopened.resolve(key)

    assert identity is not None
    assert identity.caller_id == "alice"
