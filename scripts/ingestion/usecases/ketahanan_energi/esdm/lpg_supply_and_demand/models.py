"""Pydantic schema — 6.2.9 LPG Supply and Demand (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Komponen neraca LPG, mis. Production - Gas Refinery, Production - Oil Refinery, Production - Total, Export, Import, Sales")
    nilai: str | None = Field(default=None, alias="nilai", description="Volume LPG per kategori dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="Ton")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

