"""Pydantic schema — Upah Minimum Provinsi (UMP) (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi.")
    nilai_ump: float | None = Field(default=None, alias="Nilai_UMP", description="Besaran UMP dalam Rupiah.")

    model_config = {"populate_by_name": True, "extra": "ignore"}

