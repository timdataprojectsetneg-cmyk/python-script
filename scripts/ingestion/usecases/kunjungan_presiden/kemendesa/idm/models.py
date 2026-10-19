"""Pydantic schema for Kemendesa Indeks Desa Membangun (IDM)."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KemendesaIdmRecord(BaseModel):
    id_kabupaten: Optional[str] = Field(
        default=None,
        description="Kode wilayah administrasi kabupaten/kota (misal: 3302)."
    )
    provinsi: str = Field(
        description="Nama provinsi wilayah administrasi."
    )
    kabupaten_kota: str = Field(
        description="Nama kabupaten/kota wilayah administrasi."
    )
    total_desa: int = Field(
        default=0,
        description="Total jumlah desa di wilayah kabupaten/kota."
    )
    total_kecamatan: Optional[int] = Field(
        default=None,
        description="Total jumlah kecamatan di wilayah kabupaten/kota."
    )
    desa_mandiri: int = Field(
        default=0,
        description="Estimasi / jumlah desa berstatus Mandiri."
    )
    desa_maju: int = Field(
        default=0,
        description="Estimasi / jumlah desa berstatus Maju."
    )
    desa_berkembang: int = Field(
        default=0,
        description="Estimasi / jumlah desa berstatus Berkembang."
    )
    desa_tertinggal: int = Field(
        default=0,
        description="Estimasi / jumlah desa berstatus Tertinggal."
    )
    desa_sangat_tertinggal: int = Field(
        default=0,
        description="Estimasi / jumlah desa berstatus Sangat Tertinggal."
    )
    indeks_ketahanan_sosial: Optional[float] = Field(
        default=None,
        description="Rata-rata skor ketahanan sosial (IKS) desa."
    )
    indeks_ketahanan_ekonomi: Optional[float] = Field(
        default=None,
        description="Rata-rata skor ketahanan ekonomi (IKE) desa."
    )
    indeks_ketahanan_lingkungan: Optional[float] = Field(
        default=None,
        description="Rata-rata skor ketahanan ekologi/lingkungan (IKL) desa."
    )
    skor_idm: Optional[float] = Field(
        default=None,
        description="Skor komposit Indeks Desa Membangun (rata-rata IKS, IKE, IKL)."
    )
    status_idm: Optional[str] = Field(
        default="BERKEMBANG",
        description="Klasifikasi status IDM wilayah (MANDIRI, MAJU, BERKEMBANG, TERTINGGAL, SANGAT TERTINGGAL)."
    )
    tahun: int = Field(
        default=2024,
        description="Tahun penilaian IDM."
    )
    data_source: str = Field(
        default="Kementerian Desa PDTT - IDM Open API",
        description="Sumber resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = KemendesaIdmRecord
