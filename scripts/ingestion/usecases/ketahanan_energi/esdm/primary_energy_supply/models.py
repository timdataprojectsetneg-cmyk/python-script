"""Pydantic schema — Primary Energy Supply (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun pasokan energi primer (grafik 2019–2025)")
    jenis_energi: str | None = Field(default=None, alias="jenis_energi", description="Crude Oil & Product, Natural Gas & Product, Coal, NRE (New and Renewable Energy), atau Total")
    pasokan: str | None = Field(default=None, alias="pasokan", description="Pasokan energi primer per jenis energi")
    pangsa_persen: str | None = Field(default=None, alias="pangsa_persen", description="Porsi terhadap total pasokan energi primer tahun tersebut (diagram donat)")
    pertumbuhan_yoy_persen: str | None = Field(default=None, alias="pertumbuhan_yoy_persen", description="Pertumbuhan dibanding tahun sebelumnya, dari teks ringkasan")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

