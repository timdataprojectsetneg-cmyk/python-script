"""Pydantic schema — 5.2.2 Energy Consumption in Household Sector in Energy Unit (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Jenis energi yang dikonsumsi sektor rumah tangga, mis. Traditional Biomass, Gas, Kerosene, LPG, Biogas, Electricity, Total")
    nilai: str | None = Field(default=None, alias="nilai", description="Konsumsi energi per kategori dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="Thousand BOE")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

