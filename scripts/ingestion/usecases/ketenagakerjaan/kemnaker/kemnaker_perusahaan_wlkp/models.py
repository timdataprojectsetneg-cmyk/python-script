"""Pydantic schema — Kemnaker Perusahaan WLKP (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (\"Jumlah\" = nasional).")
    mikro: int | None = Field(default=None, alias="skala_perusahaan_mikro", description="Perusahaan terlapor WLKP skala Mikro (1–4 TK).")
    kecil: int | None = Field(default=None, alias="skala_perusahaan_kecil", description="Perusahaan terlapor WLKP skala Kecil (5–19 TK).")
    menengah: int | None = Field(default=None, alias="skala_perusahaan_menengah", description="Perusahaan terlapor WLKP skala Menengah (20–99 TK).")
    besar: int | None = Field(default=None, alias="skala_perusahaan_besar", description="Perusahaan terlapor WLKP skala Besar (≥100 TK).")
    belum_teridentifikasi: int | None = Field(default=None, alias="skala_perusahaan_belum_teridentifikasi", description="Perusahaan terlapor WLKP yang belum melaporkan informasi tenaga kerja.")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total seluruh skala.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
