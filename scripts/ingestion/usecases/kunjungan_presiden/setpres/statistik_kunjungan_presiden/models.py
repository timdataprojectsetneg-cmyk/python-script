"""Pydantic schema for Setpres Statistik Kunjungan Kerja Presiden."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SetpresStatistikKunjunganRecord(BaseModel):
    provinsi: str = Field(
        description="Nama provinsi wilayah kerja tempat kunjungan Presiden berlangsung."
    )
    kabupaten_kota: str = Field(
        description="Nama kabupaten atau kota tempat pelaksanaan kunjungan Presiden."
    )
    frekuensi_kunjungan_total: int = Field(
        description="Jumlah frekuensi kumulatif kunjungan kerja Presiden ke daerah bersangkutan."
    )
    kunjungan_terakhir: Optional[str] = Field(
        default=None,
        description="Waktu atau tanggal pelaksanaan rangkaian kunjungan kerja terbaru (format: 'YYYY-MM-DD' atau deskriptif)."
    )
    agenda_utama: Optional[str] = Field(
        default=None,
        description="Fokus agenda utama kegiatan Presiden (misal: peresmian infrastruktur, peninjauan pangan, bansos)."
    )
    durasi_kunjungan_hari: Optional[int] = Field(
        default=1,
        description="Durasi pelaksanaan rangkaian kunjungan kerja dalam satuan hari."
    )
    pejabat_pendamping_utama: Optional[str] = Field(
        default=None,
        description="Daftar menteri, pejabat tinggi negara, atau pimpinan lembaga pendamping Presiden."
    )
    data_source: str = Field(
        default="Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = SetpresStatistikKunjunganRecord
