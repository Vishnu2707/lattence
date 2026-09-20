from lattence.governance import AuditLog, default_audit_db_path
from lattence.graph import JsonValue


def record_api_audit_event(
    *,
    caller_id: str,
    action: str,
    target: str,
    result: str,
    details: dict[str, JsonValue] | None = None,
) -> None:
    log = AuditLog(default_audit_db_path())
    log.record(
        actor=caller_id, action=action, target=target, result=result, details=details
    )
