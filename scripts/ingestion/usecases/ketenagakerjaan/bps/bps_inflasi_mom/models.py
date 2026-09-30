"""Pydantic schema — BPS Inflasi MoM (API)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Record(BaseModel):
    period: str | None = Field(default=None, description='e.g. "2026-08"')
    inflation_mom: float | None = Field(default=None, alias="Inflasi_MoM")

    model_config = {"populate_by_name": True, "extra": "ignore"}
