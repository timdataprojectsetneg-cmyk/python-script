"""Pydantic schema — 3.1 Primary Energy Supply by Sources (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Kapasitas Terpasang (Gambar 7) atau Produksi Listrik (Gambar 8)")
    jenis_pembangkit: str | None = Field(default=None, alias="jenis_pembangkit", description="NRE PP, Steam PP, Gas PP, Combined Cycle PP, Diesel PP, Gas Engine PP, atau Total")
    nilai: str | None = Field(default=None, alias="nilai", description="Kapasitas atau produksi per jenis pembangkit")
    satuan: str | None = Field(default=None, alias="satuan", description="GW (kapasitas), TWh (produksi)")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
