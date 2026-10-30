"""Pydantic schema — 6.4.3 Import of Electricity (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Jenis pembangkit sumber listrik impor, mis. Hydro PP")
    nilai: str | None = Field(default=None, alias="nilai", description="Energi listrik impor per kategori dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="GWh")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

