"""Pydantic schema for Kemlu Rekapitulasi Kasus WNI."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class KemluKasusWniRecord(BaseModel):
    id_kasus: str = Field(
        description="Nomor registrasi/tiket kasus pelindungan WNI (misal: 'PWNI-2026-MY-412')."
    )
    negara_kejadian: str = Field(
        description="Negara tempat timbulnya kasus hukum, ketenagakerjaan, atau keimigrasian."
    )
    kategori_kasus: str = Field(
        description="Kategori kasus (Gaji Tidak Dibayar, Keimigrasian, TPPO / Online Scam, dsb)."
    )
    jumlah_korban_terlibat: int = Field(
        default=1,
        description="Jumlah estimasi WNI korban atau pihak terkait."
    )
    tanggal_pengaduan: Optional[str] = Field(
        default=None,
        description="Waktu tanggal laporan diterima perwakilan RI (format: 'YYYY-MM-DD')."
    )
    status_penanganan: str = Field(
        default="Dalam Proses",
        description="Status penanganan kasus (Dalam Proses, Mediasi Selesai, Repatriasi Selesai)."
    )
    bantuan_hukum_diberikan: Optional[str] = Field(
        default=None,
        description="Bentuk advokasi diplomatik, pendampingan hukum retainer, atau safe house."
    )
    data_source: str = Field(
        default="Kementerian Luar Negeri RI (Direktorat Pelindungan WNI / BHI)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = KemluKasusWniRecord
