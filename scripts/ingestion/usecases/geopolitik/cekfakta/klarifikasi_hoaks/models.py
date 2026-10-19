"""Pydantic schema for CekFakta Klarifikasi Hoaks."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CekfaktaKlarifikasiHoaksRecord(BaseModel):
    id_narasi: str = Field(
        description="Identifier pemantauan narasi internasional (misal: 'NAR-2026-01')."
    )
    isu_pemberitaan: str = Field(
        description="Isu atau topik pemberitaan geopolitik mengenai Indonesia."
    )
    klaim_narasi: str = Field(
        description="Substansi narasi yang beredar di media massa internasional atau ruang publik."
    )
    asal_media_sumber: Optional[str] = Field(
        default=None,
        description="Media internasional atau platform media sosial asal narasi."
    )
    tingkat_sebaran: str = Field(
        default="Sedang",
        description="Tingkat persebaran isu (Tinggi / Viral, Sedang, Rendah)."
    )
    hasil_verifikasi_cek_fakta: str = Field(
        default="Konteks Dimanipulasi",
        description="Hasil verifikasi fakta (Fakta, Misinformasi, Konteks Dimanipulasi, Disinformasi)."
    )
    tanggapan_resmi_pemerintah: Optional[str] = Field(
        default=None,
        description="Substansi tanggapan dan klarifikasi resmi pemerintah."
    )
    instansi_klarifikasi: Optional[str] = Field(
        default="Kementerian Luar Negeri RI & Komdigi",
        description="Instansi juru bicara pemerintah."
    )
    tanggal_klarifikasi: Optional[str] = Field(
        default=None,
        description="Waktu publikasi klarifikasi resmi (format YYYY-MM-DD)."
    )
    data_source: str = Field(
        default="CekFakta.com, Kementerian Luar Negeri RI & Kementerian Komunikasi dan Digital",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = CekfaktaKlarifikasiHoaksRecord
