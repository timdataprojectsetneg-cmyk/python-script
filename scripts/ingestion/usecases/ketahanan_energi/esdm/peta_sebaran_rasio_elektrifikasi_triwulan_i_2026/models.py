"""Pydantic schema — ESDM - PETA SEBARAN RASIO ELEKTRIFIKASI (RE) TRIWULAN I 2026 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Periode data peta, mis. Triwulan I 2026")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi sebagaimana tertulis pada peta (huruf kapital)")
    re_pln_persen: str | None = Field(default=None, alias="RE PLN", description="Rasio elektrifikasi PLN per provinsi (angka biru pada peta)")
    re_nas_persen: str | None = Field(default=None, alias="RE NAS", description="Rasio elektrifikasi nasional per provinsi (angka merah pada peta)")
    satuan: str | None = Field(default=None, alias="Satuan", description="Satuan nilai RE: %")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
