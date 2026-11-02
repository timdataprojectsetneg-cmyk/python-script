"""Pydantic schema — BPS Inflasi YoY (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Bulan dan tahun.")
    inflasi_yoy: float | None = Field(default=None, alias="Inflasi_YoY", description="Inflasi year-on-year nasional.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
