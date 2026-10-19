"""Pydantic schema for Setpres Pertemuan Bilateral."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SetpresPertemuanBilateralRecord(BaseModel):
    id_pertemuan: str = Field(
        description="Kode registrasi pertemuan diplomatik (misal: 'BIL-2026-01')."
    )
    tanggal_kegiatan: Optional[str] = Field(
        default=None,
        description="Waktu pertemuan berlangsung (format YYYY-MM-DD)."
    )
    negara_mitra: str = Field(
        description="Negara mitra pertemuan diplomatik."
    )
    lokasi_kota_negara: str = Field(
        description="Tempat terselenggaranya pertemuan (misal: 'Istana Singapura', 'Canberra, Australia')."
    )
    format_pertemuan: str = Field(
        default="Pertemuan Bilateral",
        description="Format (Kunjungan Kenegaraan, KTT Bilateral, Pertemuan Bilateral Sela-sela)."
    )
    tokoh_pemimpin_mitra: str = Field(
        description="Nama Presiden / Perdana Menteri / Kepala Negara mitra."
    )
    isu_utama_dibahas: Optional[str] = Field(
        default=None,
        description="Fokus substansi bahasan diplomatik (Investasi EBT, Kerja Sama Hankam, IKN)."
    )
    kesepakatan_konkret: Optional[str] = Field(
        default=None,
        description="Hasil deliverables atau dokumen kerja sama yang disepakati."
    )
    data_source: str = Field(
        default="Sekretariat Presiden RI & Kementerian Luar Negeri RI",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = SetpresPertemuanBilateralRecord
