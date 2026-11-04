"""Pydantic schema — 6.1.2 Coal Supply (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):

    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data pada tabel")
    production_steam_coal_ton: str | None = Field(default=None, alias="Production Steam Coal (Ton)", description="Jumlah produksi steam coal.")
    export_ton: str | None = Field(default=None, alias="Export (Ton)", description="Jumlah ekspor komoditas/produk.")
    import_ton: str | None = Field(default=None, alias="Import (Ton)", description="Jumlah impor komoditas/produk.")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
