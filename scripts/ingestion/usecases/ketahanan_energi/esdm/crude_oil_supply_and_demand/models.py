"""Pydantic schema — 6.2.3 Crude Oil Supply and Demand (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Komponen neraca minyak bumi, mis. Production")
    nilai: str | None = Field(default=None, alias="nilai", description="Volume minyak bumi per kategori dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="Thousand bbl")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
