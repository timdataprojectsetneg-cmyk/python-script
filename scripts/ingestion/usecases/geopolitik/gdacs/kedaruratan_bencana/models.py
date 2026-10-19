"""Pydantic schema mirroring the Data Dictionary for GDACS Global Disaster Alerts."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GdacsKedaruratanBencanaRecord(BaseModel):
    id_peringatan: str = Field(
        description="Identifier unik kedaruratan bencana internasional (misal: EQ1571367, TC1001337)."
    )
    nama_kejadian: str = Field(
        description="Nama bencana alam atau kedaruratan kesehatan global."
    )
    negara_kawasan: str = Field(
        description="Negara atau wilayah geografis terdampak bencana."
    )
    jenis_kedaruratan: str = Field(
        description="Kategori bencana (Gempa Bumi, Siklon Tropis, Tsunami, Banjir, Letusan Gunung Api, Kebakaran Hutan)."
    )
    level_waspada: str = Field(
        default="Green Alert",
        description="Status tingkat risiko resmi: Red Alert, Orange Alert, Green Alert."
    )
    tanggal_kejadian: str = Field(
        description="Waktu awal bencana terdeteksi dalam format ISO YYYY-MM-DD."
    )
    estimasi_korban_terdampak: Optional[int] = Field(
        default=None,
        description="Estimasi jumlah populasi warga yang terdampak langsung (jiwa)."
    )
    potensi_imbas_ke_indonesia: Optional[str] = Field(
        default=None,
        description="Analisis potensi dampak terhadap keselamatan WNI di wilayah, jalur logistik pelayaran, atau pasokan impor pangan."
    )
    latitude: Optional[float] = Field(
        default=None,
        description="Titik koordinat garis lintang pusat bencana."
    )
    longitude: Optional[float] = Field(
        default=None,
        description="Titik koordinat garis bujur pusat bencana."
    )
    severity: Optional[str] = Field(
        default=None,
        description="Tingkat keparahan parameter teknis bencana (magnitudo, kecepatan angin, luas area)."
    )
    kode_event: Optional[str] = Field(
        default=None,
        description="Kode tipe kejadian GDACS (EQ, TC, TS, FL, VO, WF, DR)."
    )
    deskripsi: Optional[str] = Field(
        default=None,
        description="Ringkasan narasi resmi kejadian bencana GDACS."
    )
    link_detail: Optional[str] = Field(
        default=None,
        description="Tautan laporan analisis spasial bencana GDACS."
    )
    data_source: str = Field(
        default="Global Disaster Alert and Coordination System (GDACS)",
        description="Sumber resmi data kedaruratan bencana global."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = GdacsKedaruratanBencanaRecord
