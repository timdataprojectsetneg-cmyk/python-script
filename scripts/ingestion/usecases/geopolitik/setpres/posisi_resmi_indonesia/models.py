"""Pydantic schema for Posisi Resmi Indonesia (official statements, one row per issue passage)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PosisiResmiIndonesiaRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    tanggal_pernyataan: Optional[date] = Field(
        default=None, alias="Tanggal Pernyataan", description="Tanggal pernyataan pers."
    )
    pejabat: Optional[str] = Field(default=None, alias="Pejabat", description="Penyampai posisi resmi.")
    forum_konteks: Optional[str] = Field(
        default=None, alias="Forum/Konteks", description="Konteks pernyataan (judul siaran + lokasi)."
    )
    isu: str = Field(alias="Isu", description="Isu yang dipisahkan dari isi pidato (klasifikasi kata kunci).")
    posisi_yang_dinyatakan: str = Field(
        alias="Posisi yang Dinyatakan",
        description="Kutipan ekstraktif bagian pernyataan yang memuat isu (tanpa inferensi sentimen).",
    )
    urutan_isu: Optional[int] = Field(
        default=None,
        description="Nomor urut blok isu dalam satu siaran pers (tambahan dari hasil crawl; kunci unik bersama url_sumber).",
    )
    url_sumber: Optional[str] = Field(
        default=None, description="Tautan siaran pers Setneg (tambahan dari hasil crawl, tidak ada di kamus Excel)."
    )


Record = PosisiResmiIndonesiaRecord
