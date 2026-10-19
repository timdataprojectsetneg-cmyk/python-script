"""Pydantic schema for Kemenkop SIMKOPDES (Koperasi Desa Merah Putih)."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KemenkopSimkopdesKdmpRecord(BaseModel):
    provinsi: str = Field(
        description="Nama provinsi wilayah kerja (misal: 'JAWA TIMUR')."
    )
    provinsi_id: Optional[int] = Field(
        default=None,
        description="Kode ID provinsi Kemendagri / Simkopdes."
    )
    kabupaten_kota: str = Field(
        description="Nama kabupaten atau kota lokasi koperasi."
    )
    total_koperasi: int = Field(
        default=0,
        description="Jumlah unit Koperasi Desa Merah Putih terbentuk."
    )
    koperasi_sehat: int = Field(
        default=0,
        description="Jumlah koperasi berpredikat sehat."
    )
    koperasi_cukup_sehat: int = Field(
        default=0,
        description="Jumlah koperasi berpredikat cukup sehat."
    )
    koperasi_tidak_sehat: int = Field(
        default=0,
        description="Jumlah koperasi belum/tidak sehat."
    )
    total_anggota: int = Field(
        default=0,
        description="Total anggota masyarakat terdaftar."
    )
    omzet_pendapatan: float = Field(
        default=0.0,
        description="Akumulasi perputaran pendapatan koperasi dalam Rupiah."
    )
    latitude: Optional[float] = Field(
        default=None,
        description="Titik koordinat lintang lokasi sentra koperasi."
    )
    longitude: Optional[float] = Field(
        default=None,
        description="Titik koordinat bujur lokasi sentra koperasi."
    )
    data_source: str = Field(
        default="Kementerian Koperasi RI (Sistem Informasi Manajemen Koperasi Desa / SIMKOPDES)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = KemenkopSimkopdesKdmpRecord
