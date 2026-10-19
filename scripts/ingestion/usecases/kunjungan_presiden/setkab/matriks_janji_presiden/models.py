"""Pydantic schema for Setkab Matriks Janji & Arahan Presiden."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SetkabMatriksJanjiRecord(BaseModel):
    id_komitmen: str = Field(
        description="Identifier resmi komitmen janji/arahan Presiden (misal: 'JNJ-2026-001')."
    )
    program_strategis: str = Field(
        description="Rumpun program atau sektor strategis prioritas Presiden."
    )
    substansi_komitmen: str = Field(
        description="Uraian isi komitmen atau arahan kerja spesifik Presiden."
    )
    tanggal_penyampaian: Optional[str] = Field(
        default=None,
        description="Tanggal penyampaian komitmen/arahan (format: 'YYYY-MM-DD' atau deskriptif)."
    )
    forum_agenda: Optional[str] = Field(
        default=None,
        description="Konteks seremonial kunjungan, rapat terbatas, atau forum kenegaraan."
    )
    provinsi: Optional[str] = Field(
        default=None,
        description="Provinsi sasaran program atau lokasi kunjungan."
    )
    kabupaten_kota: Optional[str] = Field(
        default=None,
        description="Kabupaten/Kota target penerima manfaat."
    )
    desa_lokasi: Optional[str] = Field(
        default=None,
        description="Lokasi titik desa/kawasan fisik peninjauan proyek."
    )
    kl_penanggung_jawab: Optional[str] = Field(
        default=None,
        description="Kementerian / Lembaga pengampu eksekusi program."
    )
    status_pemenuhan: str = Field(
        default="On Progress",
        description="Status pelaksanaan komitmen (misal: 'Selesai', 'On Progress', 'Terkendala')."
    )
    catatan_progres_sekdukkab: Optional[str] = Field(
        default=None,
        description="Catatan perkembangan monitoring Tim Dukungan Kerja Kabinet (Sekdukkab)."
    )
    koordinasi_kemenko: Optional[str] = Field(
        default=None,
        description="Kementerian Koordinator pembina penyelesaian komitmen."
    )
    data_source: str = Field(
        default="Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = SetkabMatriksJanjiRecord
