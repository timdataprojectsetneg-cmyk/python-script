"""Pydantic schema — Final Energy Consumption (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data pada tabel konsumsi energi final per jenis energi (2015-2025).")
    traditional_biomass: str | None = Field(default=None, alias="Traditional Biomass", description="Konsumsi energi dari biomassa tradisional.")
    industrial_biomass: str | None = Field(default=None, alias="Industrial Biomass", description="Konsumsi energi dari biomassa industri.")
    solar_water_heater: str | None = Field(default=None, alias="Solar Water Heater", description="Konsumsi energi dari pemanas air tenaga surya. Bernilai \"n.a\" pada 2015-2021.")
    direct_use_of_geothermal: str | None = Field(default=None, alias="Direct Use of Geothermal", description="Konsumsi energi dari pemanfaatan langsung panas bumi. Bernilai \"n.a\" pada 2015-2021.")
    coal: str | None = Field(default=None, alias="Coal", description="Konsumsi energi dari batu bara. Memiliki catatan 1).")
    natural_gas: str | None = Field(default=None, alias="Natural Gas", description="Konsumsi energi dari gas alam.")
    oil_fuel: str | None = Field(default=None, alias="Oil Fuel", description="Konsumsi energi dari bahan bakar minya")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

