"""Pydantic schema — 5.1.2 Energy Consumption in Industrial Sector in Energy Unit (mirrors the Data Dictionary)."""
from datetime import date as DateType

from pydantic import BaseModel, Field


class Record(BaseModel):

    year: DateType | None = Field(default=None, alias="Year", description="Tahun pengamatan konsumsi energi, yaitu 2015–2025.")
    industrial_biomass: str | None = Field(default=None, alias="Industrial Biomass", description="Konsumsi energi yang berasal dari biomassa industri pada tahun tertentu.")
    direct_use_geothermal: str | None = Field(default=None, alias="Direct Use Geothermal", description="Konsumsi energi panas bumi yang digunakan secara langsung pada tahun tertentu.")
    coal: str | None = Field(default=None, alias="Coal", description="Konsumsi energi yang berasal dari batu bara pada tahun tertentu.")
    briquette: str | None = Field(default=None, alias="Briquette", description="Konsumsi energi yang berasal dari briket pada tahun tertentu.")
    gas: str | None = Field(default=None, alias="Gas", description="Konsumsi energi yang berasal dari gas pada tahun tertentu.")
    kerosene: str | None = Field(default=None, alias="Kerosene", description="Konsumsi energi yang berasal dari minyak tanah pada tahun tertentu.")
    gasoline_ron_90: str | None = Field(default=None, alias="Gasoline RON 90", description="Konsumsi bensin RON 90 pada tahun tertentu.")
    gasoline_ron_92: str | None = Field(default=None, alias="Gasoline RON 92", description="Konsumsi bensin RON 92 pada tahun tertentu.")
    gasoline_ron_95_98_100: str | None = Field(default=None, alias="Gasoline RON 95+98+100", description="Konsumsi bensin dengan RON 95, 98, dan 100 pada tahun tertentu.")
    gasoil_cn_48: str | None = Field(default=None, alias="Gasoil CN 48", description="Konsumsi gasoil dengan CN 48 pada tahun tertentu.")
    bio_gasoil: str | None = Field(default=None, alias="Bio Gasoil", description="Konsumsi bio-gasoil pada tahun tertentu.")
    gasoil_cn_51: str | None = Field(default=None, alias="Gasoil CN 51", description="Konsumsi gasoil dengan CN 51 pada tahun tertentu.")
    gasoil_cn_53: str | None = Field(default=None, alias="Gasoil CN 53", description="Konsumsi gasoil dengan CN 53 pada tahun tertentu.")
    mdf: str | None = Field(default=None, alias="MDF", description="Konsumsi MDF pada tahun tertentu.")
    fuel_oil: str | None = Field(default=None, alias="Fuel Oil", description="Konsumsi fuel oil pada tahun tertentu.")
    lpg: str | None = Field(default=None, alias="LPG", description="Konsumsi LPG pada tahun tertentu.")
    electricity: str | None = Field(default=None, alias="Electricity", description="Konsumsi energi listrik pada tahun tertentu.")
    total_oil_fuel: str | None = Field(default=None, alias="Total Oil Fuel", description="Total konsumsi kelompok oil fuel pada tahun tertentu.")
    total: str | None = Field(default=None, alias="Total", description="Total konsumsi energi pada tahun tertentu.")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
