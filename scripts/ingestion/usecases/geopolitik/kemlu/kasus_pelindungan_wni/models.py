"""Pydantic schema for Kemlu Kasus Pelindungan WNI (LKJ Dit. PWNI)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KasusPelindunganWniRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    tahun: Optional[int] = Field(
        default=None,
        alias="Tahun",
        description="Tahun laporan kinerja.",
    )
    kelompok_kasus: Optional[str] = Field(
        default=None,
        alias="Kelompok Kasus",
        description="Kelompok pada Matriks Informasi Kinerja.",
    )
    jenis_kasus: Optional[str] = Field(
        default=None,
        alias="Jenis Kasus",
        description="Subjenis kasus sesuai label lampiran.",
    )
    ditangani: Optional[int] = Field(
        default=None,
        alias="Ditangani",
        ge=0,
        description="Angka kolom ditangani, dipertahankan meski terdapat anomali antarbagian.",
    )
    selesai: Optional[int] = Field(
        default=None,
        alias="Selesai",
        ge=0,
        description="Angka kolom selesai. Tidak diasumsikan cohort yang sama dengan ditangani.",
    )
    halaman_pdf: Optional[int] = Field(
        default=None,
        alias="Halaman PDF",
        description="Halaman PDF tabel sumber.",
    )


Record = KasusPelindunganWniRecord
