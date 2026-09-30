"""Pydantic schema — BPS Inflasi YoY (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    periode: str | None = Field(default=None, alias="Periode")
    inflasi_yoy: float | None = Field(default=None, alias="Inflasi_YoY")
    inflasi_mtm: float | None = Field(default=None, alias="Inflasi_MtM")
    komponen_pendorong: str | None = Field(default=None, alias="Komponen_Pendorong")

    model_config = {"populate_by_name": True, "extra": "ignore"}

