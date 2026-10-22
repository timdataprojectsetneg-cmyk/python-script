"""Pydantic schema — Kemnaker Perusahaan Skala Upah Table 1 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (\"Jumlah\" = nasional).")
    mikro: int | None = Field(default=None, alias="Mikro", description="Perusahaan yang melaporkan Struktur Skala Upah skala Mikro (1–4 TK).")
    kecil: int | None = Field(default=None, alias="Kecil", description="Perusahaan yang melaporkan Struktur Skala Upah skala Kecil (5–19 TK).")
    menengah: int | None = Field(default=None, alias="Menengah", description="Perusahaan yang melaporkan Struktur Skala Upah skala Menengah (20–99 TK).")
    besar: int | None = Field(default=None, alias="Besar", description="Perusahaan yang melaporkan Struktur Skala Upah skala Besar (≥100 TK).")
    tidak_teridentifikasi: int | None = Field(default=None, alias="Tidak_Teridentifikasi", description="Perusahaan yang melaporkan Struktur Skala Upah yang belum melaporkan informasi tenaga kerja.")
    tahun: str | None = Field(default=None, alias="tahun", description="Tahun Pelaporan")
    bulan: str | None = Field(default=None, alias="bulan", description="Bulan Pelaporan")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total seluruh skala.")

    model_config = {"populate_by_name": True, "extra": "ignore"}

