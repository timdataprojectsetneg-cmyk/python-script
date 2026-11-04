"""Pydantic schema — 6.2.6 Import of Refined Products (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):

    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data")
    avtur: str | None = Field(default=None, alias="Avtur", description="Volume impor Avtur per tahun")
    avgas: str | None = Field(default=None, alias="Avgas", description="Volume impor Avgas per tahun")
    gasoline_ron_88_90: str | None = Field(default=None, alias="Gasoline RON 88 & 90", description="Volume impor Bensin RON 88 & 90 per tahun")
    gasoline_ron_95: str | None = Field(default=None, alias="Gasoline RON 95", description="Volume impor Bensin RON 95 per tahun")
    gasoline_ron_92: str | None = Field(default=None, alias="Gasoline RON 92", description="Volume impor Bensin RON 92 per tahun")
    naphtha: str | None = Field(default=None, alias="Naphtha", description="Volume impor Naphtha per tahun")
    homc: str | None = Field(default=None, alias="HOMC", description="Volume impor HOMC per tahun")
    gasoil: str | None = Field(default=None, alias="Gasoil", description="Volume impor Gasoil per tahun")
    fuel_oil: str | None = Field(default=None, alias="Fuel Oil", description="Volume impor Fuel Oil per tahun")
    mdf: str | None = Field(default=None, alias="MDF", description="Volume impor MDF per tahun")
    total_oil_fuel: str | None = Field(default=None, alias="Total Oil Fuel", description="Total impor seluruh jenis BBM per tahun")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
