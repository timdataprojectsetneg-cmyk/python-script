"""Pydantic schema for Kemendagri Susunan Pemerintahan Daerah."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KemendagriSusunanPemdaRecord(BaseModel):
    kode_daerah: str = Field(
        description="Kode wilayah administrasi Kemendagri (misal: '33.02')."
    )
    provinsi: str = Field(
        description="Nama provinsi tempat kabupaten/kota berada."
    )
    kabupaten_kota: str = Field(
        description="Nama kabupaten atau kota administrasi."
    )
    nama_kepala_daerah: str = Field(
        description="Nama lengkap Bupati / Walikota / Gubernur / Penjabat Kepala Daerah."
    )
    status_jabatan: str = Field(
        default="Definitif",
        description="Status jabatan kepala daerah (Definitif, Penjabat / Pj, Pelaksana Tugas / Plt)."
    )
    partai_pengusung_koalisi: Optional[str] = Field(
        default=None,
        description="Partai politik atau koalisi pengusung kepala daerah terpilih."
    )
    nama_ketua_dprd: Optional[str] = Field(
        default=None,
        description="Nama Ketua DPRD Kabupaten/Kota."
    )
    partai_ketua_dprd: Optional[str] = Field(
        default=None,
        description="Partai politik asal Ketua DPRD."
    )
    komposisi_kursi_dprd: Optional[str] = Field(
        default=None,
        description="Distribusi perolehan kursi partai di DPRD (ringkasan tekstual)."
    )
    data_source: str = Field(
        default="Kementerian Dalam Negeri RI (Ditjen Otonomi Daerah & Pusdatin PELITA)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry
Record = KemendagriSusunanPemdaRecord
