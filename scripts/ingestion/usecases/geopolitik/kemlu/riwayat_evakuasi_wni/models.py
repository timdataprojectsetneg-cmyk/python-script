"""Pydantic schema for Kemlu Riwayat Evakuasi WNI (Renstra Dit. PWNI 2025-2029)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RiwayatEvakuasiWniRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    tahun: Optional[int] = Field(
        default=None,
        alias="Tahun",
        description="Tahun evakuasi historis.",
    )
    negara_wilayah: Optional[str] = Field(
        default=None,
        alias="Negara/Wilayah",
        description="Negara atau gabungan negara pada ringkasan sumber, dipisah titik koma.",
    )
    konteks: Optional[str] = Field(
        default=None,
        alias="Konteks",
        description="Kolom 'Jenis Kondisi' sumber (mis. Perang/Konflik); bukan tingkat risiko.",
    )
    wni_dievakuasi: Optional[int] = Field(
        default=None,
        alias="WNI Dievakuasi",
        ge=0,
        description="Jumlah WNI pada ringkasan tahunan.",
    )
    wna_dievakuasi: Optional[int] = Field(
        default=None,
        alias="WNA Dievakuasi",
        ge=0,
        description="Jumlah WNA jika disebutkan; kosong bukan nol.",
    )
    halaman_pdf: Optional[int] = Field(
        default=None,
        alias="Halaman PDF",
        description="Halaman PDF tempat baris tabel berada.",
    )


Record = RiwayatEvakuasiWniRecord
