"""Pydantic schema — Upah Minimum Provinsi (UMP)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: str | None = Field(default=None, alias="Tahun")
    provinsi: str | None = Field(default=None, alias="Provinsi")
    ump: float | None = Field(default=None, alias="UMP", ge=0)

    model_config = {"populate_by_name": True, "extra": "ignore"}
