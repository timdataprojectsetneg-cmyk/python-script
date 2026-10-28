"""Pydantic schema mirroring the Data Dictionary for PMA Negara Asal."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PmaNegaraAsalRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    periode: Optional[str] = Field(
        default=None,
        alias="Periode",
        description="2025-Q4 = Oktober-Desember; 2025-YTD06 = Januari-Juni (Semester I); 2025-YTD09 = Januari-September; 2025-FY = Januari-Desember.",
    )
    peringkat: Optional[int] = Field(
        default=None, alias="Peringkat", ge=1, description="Urutan lima besar pada infografis."
    )
    negara_asal: Optional[str] = Field(
        default=None, alias="Negara Asal", description="Negara/ekonomi asal PMA sebagaimana sumber."
    )
    realisasi_pma: Optional[float] = Field(
        default=None,
        alias="Realisasi PMA",
        ge=0,
        description="Nilai realisasi investasi asing (Miliar USD), satu desimal sesuai infografis (dua desimal pada rilis 2024).",
    )
    halaman_pdf: Optional[int] = Field(
        default=None, alias="Halaman PDF", description="Nomor halaman PDF sebagai jejak verifikasi."
    )


Record = PmaNegaraAsalRecord
