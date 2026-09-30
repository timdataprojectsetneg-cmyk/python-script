"""Pydantic schema — Signal Ketenagakerjaan."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Record(BaseModel):
    title: str | None = Field(default=None)
    url: str | None = Field(default=None)
    published_at: str | None = Field(default=None, alias="Published_At")
    summary: str | None = Field(default=None)

    model_config = {"populate_by_name": True, "extra": "ignore"}
