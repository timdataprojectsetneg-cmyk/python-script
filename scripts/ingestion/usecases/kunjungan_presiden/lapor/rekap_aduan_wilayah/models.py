"""Pydantic schema for SP4N-LAPOR! Rekapitulasi Aduan Wilayah."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class LaporRekapAduanRecord(BaseModel):
    id_aduan: str = Field(
        description="Nomor tiket aduan masyarakat atau kode agregat wilayah SP4N-LAPOR (misal: ADU-2024-8812 / LAPOR-3171-2024)."
    )
    tanggal_lapor: str = Field(
        description="Waktu penyampaian laporan masyarakat (format YYYY-MM-DD)."
    )
    kategori_program: str = Field(
        default="Pelayanan Publik & Tata Kelola",
        description="Program terkait aduan (Pelayanan Publik, MBG, KDMP, Bansos, Infrastruktur, Pendidikan, Kesehatan)."
    )
    provinsi: str = Field(
        description="Nama provinsi asal aduan/pelapor."
    )
    kabupaten_kota: str = Field(
        description="Nama kabupaten/kota asal aduan masyarakat."
    )
    uraian_laporan: str = Field(
        description="Ringkasan substansi keluhan, aspirasi, atau rekapitulasi pengaduan masyarakat."
    )
    status_tindak_lanjut: str = Field(
        default="Selesai",
        description="Status progres tindak lanjut (Diverifikasi, Ditindaklanjuti, Selesai)."
    )
    instansi_tujuan: str = Field(
        description="K/L atau Pemerintah Daerah penanggung jawab penyelesaian aduan."
    )
    jumlah_aduan: int = Field(
        default=1,
        description="Total volume aduan yang tercatat pada wilayah/periode terkait."
    )
    tahun: int = Field(
        default=2024,
        description="Tahun periode pelaporan."
    )
    kode_wilayah: Optional[str] = Field(
        default=None,
        description="Kode administrasi wilayah adm2 BPS/Kemendagri (misal: 31.71)."
    )
    data_source: str = Field(
        default="SP4N-LAPOR! KemenPANRB, Kemensetneg & KSP",
        description="Sumber resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = LaporRekapAduanRecord
