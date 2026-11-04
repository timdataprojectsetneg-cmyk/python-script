"""Pydantic schema — 3.3 Final Energy Consumption by Type (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):

    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data pada tabel konsumsi energi final per sektor.")
    sector: str | None = Field(default=None, alias="Sector", description="Sektor pengguna energi: Industrial, Households, Commercial, Transportation, Other, Final Energy Consumption (total), dan Non Energy Utilization.")
    energy_consumption: str | None = Field(default=None, alias="Energy Consumption", description="Jumlah konsumsi energi pada sektor dan tahun tersebut.")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
