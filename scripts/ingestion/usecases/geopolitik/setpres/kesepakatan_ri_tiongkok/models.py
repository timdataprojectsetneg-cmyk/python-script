"""Pydantic schema for Kesepakatan RI-Tiongkok (one row per agreement named in the press release)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KesepakatanRiTiongkokRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    tanggal: Optional[date] = Field(
        default=None, alias="Tanggal", description="Tanggal penandatanganan yang diumumkan."
    )
    topik_kesepakatan: str = Field(
        alias="Topik Kesepakatan", description="Ringkasan topik dokumen, bukan judul legal yang direka."
    )
    pihak_indonesia: Optional[str] = Field(
        default=None, alias="Pihak Indonesia", description="Institusi Indonesia yang disebut sumber."
    )
    pihak_mitra: Optional[str] = Field(
        default=None, alias="Pihak Mitra", description="Institusi Tiongkok yang disebut sumber."
    )
    status_bukti: Optional[str] = Field(
        default=None,
        alias="Status Bukti",
        description="Status penandatanganan berdasarkan siaran pers, bukan status implementasi.",
    )
    urutan_kesepakatan: Optional[int] = Field(
        default=None,
        description="Nomor urut kesepakatan dalam satu siaran pers (tambahan dari hasil crawl; kunci unik bersama url_sumber).",
    )
    url_sumber: Optional[str] = Field(
        default=None, description="Tautan siaran pers Setneg (tambahan dari hasil crawl, tidak ada di kamus Excel)."
    )


Record = KesepakatanRiTiongkokRecord
