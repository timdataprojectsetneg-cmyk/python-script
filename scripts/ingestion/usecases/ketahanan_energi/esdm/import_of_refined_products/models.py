"""Pydantic schema — 6.2.6 Import of Refined Products (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Jenis produk BBM yang diimpor, mis. Avgas, Avtur, Gasoil, Total Oil Fuel")
    nilai: str | None = Field(default=None, alias="nilai", description="Volume impor per jenis produk dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="Thousand KL")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

