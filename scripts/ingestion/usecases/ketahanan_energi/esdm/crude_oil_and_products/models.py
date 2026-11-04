"""Pydantic schema — Crude Oil and Products (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    produk: str | None = Field(default=None, alias="produk", description="Crude Oil, Oil Fuel (BBM), atau LPG")
    komponen: str | None = Field(default=None, alias="komponen", description="Production, Export, Import, atau Domestic. Export digambar negatif di bawah sumbu")
    nilai: str | None = Field(default=None, alias="nilai", description="Nilai per komponen")
    satuan: str | None = Field(default=None, alias="satuan", description="Million Barrel (crude), Thousand Barrel (oil fuel, Gambar 4), Thousand MTon (LPG, Gambar 5)")
    pertumbuhan_yoy_persen: str | None = Field(default=None, alias="pertumbuhan_yoy_persen", description="Pertumbuhan dibanding tahun sebelumnya, dari teks. Kosong bila tidak disebut")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
