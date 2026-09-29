"""Pydantic schema — BPS Inflasi YoY (press release scrape)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Record(BaseModel):
    period: str | None = Field(default=None, description='e.g. "2026-08"')
    inflation_yoy: float | None = Field(default=None, alias="Inflasi_YoY")
    headline: str | None = Field(default=None)
    source_url: str | None = Field(default=None)

    model_config = {"populate_by_name": True, "extra": "ignore"}
