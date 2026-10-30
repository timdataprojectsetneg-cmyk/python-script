"""Pydantic schema — 6.1.2 Coal Supply (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Komponen neraca batu bara: Production, Import, atau Export")
    nilai: str | None = Field(default=None, alias="nilai", description="Volume batu bara per kategori dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="Ton")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

