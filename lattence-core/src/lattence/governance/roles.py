from enum import StrEnum


class Role(StrEnum):
    READ_FINDINGS = "read_findings"
    RUN_SCANS = "run_scans"
    RUN_ATTACKS = "run_attacks"
    MANAGE_POLICY = "manage_policy"
