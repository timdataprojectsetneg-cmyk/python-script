"""Pydantic schema for Kemlu Treaty Room (Perjanjian Internasional RI)."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KemluTreatyRoomRecord(BaseModel):
    id_perjanjian: str = Field(
        description="Nomor registrasi traktat internasional Kemenlu (misal: 'TR-2026-US-04')."
    )
    negara_mitra: str = Field(
        description="Negara pihak lawan perjanjian kerja sama bilateral."
    )
    judul_perjanjian: str = Field(
        description="Judul resmi naskah perjanjian internasional (PI)."
    )
    bidang_kerja_sama: str = Field(
        default="Ekonomi & Perdagangan",
        description="Bidang kerja sama (Hankam, Ekonomi & Energi, Maritim, Pendidikan, Kesehatan)."
    )
    tahapan: str = Field(
        default="Ditandatangani",
        description="Tahap perkembangan traktat (Negosiasi, Ditandatangani, Diratifikasi, Dilaksanakan)."
    )
    tanggal_penandatanganan: Optional[str] = Field(
        default=None,
        description="Waktu penandatanganan traktat (format: 'YYYY-MM-DD')."
    )
    dasar_pengesahan_uu_perpres: Optional[str] = Field(
        default=None,
        description="Nomor regulasi UU atau Perpres pengesahan ratifikasi traktat."
    )
    instansi_penanggung_jawab_kl: Optional[str] = Field(
        default=None,
        description="Kementerian / Lembaga teknis pengampu eksekusi kerja sama bilateral."
    )
    data_source: str = Field(
        default="Kementerian Luar Negeri RI (Direktorat Hukum dan Perjanjian Internasional / Treaty Room)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = KemluTreatyRoomRecord
