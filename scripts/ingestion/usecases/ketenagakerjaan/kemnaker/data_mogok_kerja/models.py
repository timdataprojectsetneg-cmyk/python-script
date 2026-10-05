"""Pydantic schema — Data Mogok Kerja (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    wilayah: str | None = Field(default=None, alias="Wilayah", description="Provinsi (perlu verifikasi struktur kolom sebenarnya).")
    kasus: int | None = Field(default=None, alias="Kasus", description="Jumlah kejadian mogok kerja tercatat.")
    tenaga_kerja_yang_terlibat: int | None = Field(default=None, alias="Tenaga Kerja yang Terlibat", description="Jumlah peserta mogok kerja tercatat.")
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun penarikan data")

    model_config = {"populate_by_name": True, "extra": "ignore"}

