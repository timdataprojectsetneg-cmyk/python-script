"""Pydantic schema for Setkab Tracking Arahan Lapangan."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SetkabTrackingArahanLapanganRecord(BaseModel):
    id_arahan: str = Field(
        description="Nomor registrasi arahan kerja lapangan (misal: 'ARH-2026-041')."
    )
    tanggal_arahan: Optional[str] = Field(
        default=None,
        description="Waktu penyampaian arahan saat kunjungan (format YYYY-MM-DD)."
    )
    lokasi_kunjungan: str = Field(
        description="Titik lokasi atau kabupaten/kota penyampaian instruksi presiden."
    )
    isi_arahan_presiden: str = Field(
        description="Petunjuk teknis atau instruksi Presiden kepada kementerian/lembaga atau kepala daerah."
    )
    instansi_pelaksana: str = Field(
        description="Instansi teknis kementerian/lembaga/pemda pengampu pelaksanaan tindak lanjut."
    )
    dokumen_dasar_tindak_lanjut: Optional[str] = Field(
        default=None,
        description="Surat edaran, perpres, atau keputusan menteri penindak lanjut (misal: 'Kepmentan No. 241/2026')."
    )
    status_tindak_lanjut: str = Field(
        default="Sedang Berjalan",
        description="Status pelaksanaan tindak lanjut (Tercapai, Sedang Berjalan, Perlu Koordinasi)."
    )
    data_source: str = Field(
        default="Sekretariat Kabinet RI (Deputi Bidang Persidangan Kabinet)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = SetkabTrackingArahanLapanganRecord
