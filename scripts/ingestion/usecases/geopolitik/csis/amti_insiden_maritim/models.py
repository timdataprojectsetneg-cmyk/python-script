"""Pydantic schema for CSIS AMTI Insiden Maritim Indo-Pasifik."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CsisAmtiInsidenMaritimRecord(BaseModel):
    id_insiden: str = Field(
        description="Identifier kejadian insiden maritim (misal: 'INS-AMTI-2026-08')."
    )
    tanggal_kejadian: Optional[str] = Field(
        default=None,
        description="Waktu kejadian berlangsung (format YYYY-MM-DD)."
    )
    wilayah_perairan: str = Field(
        description="Kawasan perairan strategis (Laut China Selatan, Selat Malaka, Laut Natuna Utara, dll.)."
    )
    jenis_kejadian: str = Field(
        description="Jenis insiden maritim (Manuver Kapal Milisi, Latihan Tembak Amunisi Aktif, dll.)."
    )
    pihak_terlibat: str = Field(
        description="Negara atau angkatan laut/penjaga pantai yang terlibat."
    )
    koordinat_lat: float = Field(
        default=0.0,
        description="Koordinat lintang insiden."
    )
    koordinat_lon: float = Field(
        default=0.0,
        description="Koordinat bujur insiden."
    )
    tingkat_eskalasi: str = Field(
        default="Sedang",
        description="Tingkat eskalasi ketegangan (Tinggi, Sedang, Rendah)."
    )
    catatan_analisis: Optional[str] = Field(
        default=None,
        description="Catatan implikasi terhadap jalur pelayaran nasional dan keamanan maritim."
    )
    data_source: str = Field(
        default="CSIS Asia Maritime Transparency Initiative (AMTI) & Kemhan RI",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = CsisAmtiInsidenMaritimRecord
