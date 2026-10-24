from typing import Any
from pydantic import BaseModel, Field


class OperationRequest(BaseModel):
    operation: str
    columns: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    expected_revision: int


class OperationResponse(BaseModel):
    revision: int
    affected_rows: int
    affected_cells: int
    warnings: list[str] = Field(default_factory=list)
    preview: list[dict[str, Any]] = Field(default_factory=list)
