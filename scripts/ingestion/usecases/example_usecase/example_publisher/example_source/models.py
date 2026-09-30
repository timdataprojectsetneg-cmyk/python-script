"""Pydantic schema mirroring the Data Dictionary for the example source."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExampleRecord(BaseModel):
    id: int = Field(ge=0)
    name: str
    value: float | None = None
    period: str = Field(description='Period, e.g. "2026-07"')

    model_config = {"populate_by_name": True, "extra": "ignore"}


# Registry looks up ``models.Record``.
Record = ExampleRecord
