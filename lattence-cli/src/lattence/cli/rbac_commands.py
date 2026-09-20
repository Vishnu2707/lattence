import os
from pathlib import Path
from typing import Annotated

import typer
from lattence.governance import ApiKeyStore, Role

rbac_app = typer.Typer(name="rbac", no_args_is_help=True)

_DB_ENV_VAR = "LATTENCE_RBAC_DB"
RoleOption = Annotated[list[Role], typer.Option("--role")]


def _store() -> ApiKeyStore:
    configured = os.environ.get(_DB_ENV_VAR)
    if not configured:
        raise typer.BadParameter(f"set {_DB_ENV_VAR} to the RBAC database path")
    return ApiKeyStore(Path(configured))


@rbac_app.command("create-key")
def create_key(caller_id: str, role: RoleOption) -> None:
    if not role:
        raise typer.BadParameter("pass at least one --role")
    key = _store().create_key(caller_id, frozenset(role))
    typer.echo(key)


@rbac_app.command("list")
def list_keys() -> None:
    for record in _store().list_keys():
        roles = ",".join(sorted(r.value for r in record.roles))
        typer.echo(f"{record.caller_id}  {roles}  {record.created_at}")


@rbac_app.command("revoke")
def revoke(caller_id: str) -> None:
    removed = _store().revoke_caller(caller_id)
    typer.echo(f"revoked {removed} key(s) for {caller_id}")
