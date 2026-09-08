from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

type JsonValue = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)
type NodeId = Annotated[str, StringConstraints(pattern=r"^[a-z_]+:.+$")]


def _to_utc(value: datetime) -> datetime:
    return value.astimezone(UTC)


type UtcDateTime = Annotated[datetime, AfterValidator(_to_utc)]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SourceRef(ContractModel):
    path: str
    line: int | None = Field(default=None, ge=1)
    column: int | None = Field(default=None, ge=1)
    symbol: str | None = None

    @field_validator("path")
    @classmethod
    def _validate_path(cls, value: str) -> str:
        path = PurePosixPath(value)
        if not value or path.is_absolute() or "\\" in value or ".." in path.parts:
            raise ValueError("source path must be a project-relative POSIX path")
        return value
