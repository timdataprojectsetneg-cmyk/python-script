"""Pydantic schema for Sengketa Dagang Indonesia (WTO dispute chronology, one row per milestone)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SengketaDagangIndonesiaRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    nomor_sengketa: str = Field(alias="Nomor Sengketa", description="Nomor kasus WTO (mis. DS593).")
    isu: Optional[str] = Field(default=None, alias="Isu", description="Pokok isu sengketa (judul kasus WTO).")
    tanggal_tahapan: Optional[date] = Field(
        default=None, alias="Tanggal Tahapan", description="Tanggal kejadian prosedural pada kronologi WTO."
    )
    tahapan: Optional[str] = Field(
        default=None, alias="Tahapan", description="Ringkasan tindakan pihak/DSB/panel (kalimat kronologi WTO)."
    )
    urutan_tahapan: Optional[int] = Field(
        default=None,
        alias="Urutan Tahapan",
        description="Nomor urut tahapan pada halaman kronologi kasus (tambahan dari hasil crawl; kunci unik bersama nomor_sengketa).",
    )
    url_kasus: Optional[str] = Field(
        default=None, alias="URL Kasus", description="Halaman resmi kronologi dan dokumen kasus."
    )


Record = SengketaDagangIndonesiaRecord
