"""Pydantic schema for UCDP Konflik Global (Peta Konflik Bersenjata Global)."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UcdpKonflikGlobalRecord(BaseModel):
    id_konflik: str = Field(
        description="Identifier insiden konflik bersenjata resmi UCDP (misal: 'UCDP-2026-091' atau relid)."
    )
    negara: str = Field(
        description="Negara lokasi bentrokan bersenjata."
    )
    kawasan: str = Field(
        description="Kawasan geografis konflik (misal: 'Eropa Timur', 'Afrika Utara', 'Asia')."
    )
    aktor_terlibat: str = Field(
        description="Pihak aktor yang bertikai (Pemerintah vs Pemberontak / Milisi / Sipil)."
    )
    jenis_konflik: str = Field(
        default="State-based conflict",
        description="Kategori kekerasan bersenjata (State-based, Non-state conflict, One-sided violence)."
    )
    tanggal_kejadian: Optional[str] = Field(
        default=None,
        description="Waktu insiden tanggal kejadian konflik (format: 'YYYY-MM-DD')."
    )
    jumlah_korban_tewas: int = Field(
        default=0,
        description="Jumlah korban jiwa terverifikasi (best estimate fatalities)."
    )
    koordinat_lat: Optional[float] = Field(
        default=None,
        description="Titik koordinat lintang lokasi bentrokan."
    )
    koordinat_lon: Optional[float] = Field(
        default=None,
        description="Titik koordinat bujur lokasi bentrokan."
    )
    data_source: str = Field(
        default="Uppsala Conflict Data Program (UCDP, Uppsala University)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = UcdpKonflikGlobalRecord
