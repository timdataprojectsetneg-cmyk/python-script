"""Pydantic schema — 5.2.2 Energy Consumption in Household Sector in Energy Unit (mirrors the Data Dictionary)."""
from datetime import date as DateType

from pydantic import BaseModel, Field


class Record(BaseModel):

    year: DateType | None = Field(default=None, alias="Year", description="Tahun pengamatan konsumsi energi, yaitu 2015–2025.")
    traditional_biomass: str | None = Field(default=None, alias="Traditional Biomass", description="Konsumsi energi yang berasal dari biomassa tradisional pada tahun tertentu.")
    gas: str | None = Field(default=None, alias="Gas", description="Konsumsi energi yang berasal dari gas pada tahun tertentu.")
    kerosene: str | None = Field(default=None, alias="Kerosene", description="Konsumsi energi yang berasal dari minyak tanah pada tahun tertentu.")
    lpg: str | None = Field(default=None, alias="LPG", description="Konsumsi energi yang berasal dari LPG pada tahun tertentu.")
    biogas: str | None = Field(default=None, alias="Biogas", description="Konsumsi energi yang berasal dari biogas pada tahun tertentu.")
    electricity: str | None = Field(default=None, alias="Electricity", description="Konsumsi energi listrik pada tahun tertentu.")
    total: str | None = Field(default=None, alias="Total", description="Total konsumsi energi dari seluruh jenis energi yang tercantum pada tahun tertentu.")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
