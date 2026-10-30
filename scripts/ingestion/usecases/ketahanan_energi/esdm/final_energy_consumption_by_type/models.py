"""Pydantic schema — 3.3 Final Energy Consumption by Type (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Jenis energi yang dikonsumsi, mis. Biodiesel, Coal, LPG, Electricity, Total")
    nilai: str | None = Field(default=None, alias="nilai", description="Konsumsi energi per kategori dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="Thousand BOE")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

