"""Pydantic schema for Kemlu Iuran Organisasi Internasional."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KemluIuranOrganisasiInternasionalRecord(BaseModel):
    id_organisasi: str = Field(
        description="Kode registrasi keanggotaan OI Kemenlu (misal: 'OI-UN-001')."
    )
    nama_organisasi_internasional: str = Field(
        description="Nama Organisasi Internasional (OI)."
    )
    kategori_oi: str = Field(
        default="PBB & Badan Khusus",
        description="Kategori (PBB & Badan Khusus, Kerja Sama Kawasan, Lembaga Keuangan, Komoditas)."
    )
    dasar_hukum_keanggotaan: Optional[str] = Field(
        default=None,
        description="Dasar ratifikasi / keanggotaan (Keppres/Perpres)."
    )
    kl_focal_point: str = Field(
        default="Kemenlu RI",
        description="Kementerian teknis pemegang mandat focal point RI."
    )
    besaran_iuran_tahunan_valas: float = Field(
        default=0.0,
        description="Nominal tagihan kontribusi keanggotaan."
    )
    mata_uang: str = Field(
        default="USD",
        description="Mata uang pembayaran (USD, CHF, EUR, GBP)."
    )
    ekuivalen_rupiah_miliar: float = Field(
        default=0.0,
        description="Estimasi alokasi APBN untuk pembayaran iuran (Miliar Rupiah)."
    )
    evaluasi_kemanfaatan: str = Field(
        default="Tinggi / Strategis",
        description="Hasil evaluasi berkala kemanfaatan bagi kepentingan nasional RI."
    )
    status_iuran_terakhir: str = Field(
        default="Lunas",
        description="Status pembayaran tahun berjalan (Lunas, Proses Pencairan, Tertunda)."
    )
    data_source: str = Field(
        default="Kementerian Luar Negeri RI (DJKSM) & Kementerian Keuangan RI (Perpres 30/2019)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = KemluIuranOrganisasiInternasionalRecord
