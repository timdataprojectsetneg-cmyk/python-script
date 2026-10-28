"""Pydantic schema for Target Komitmen Iklim Indonesia (Second NDC)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TargetKomitmenIklimRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    indikator: Optional[str] = Field(
        default=None,
        alias="Indikator",
        description="Indikator kuantitatif dari Second NDC.",
    )
    skenario_konteks: Optional[str] = Field(
        default=None,
        alias="Skenario/Konteks",
        description="Skenario emisi atau kebijakan pendukung yang dikutip dokumen (CPOS, LCCP_L, LCCP_H, ENDC, dst.).",
    )
    tahun_target: Optional[int] = Field(
        default=None,
        alias="Tahun Target",
        description="Horizon target/proyeksi.",
    )
    nilai_bawah: Optional[float] = Field(
        default=None,
        alias="Nilai Bawah",
        description="Batas bawah; untuk target tunggal nilainya sama dengan batas atas.",
    )
    nilai_atas: Optional[float] = Field(
        default=None,
        alias="Nilai Atas",
        description="Batas atas rentang asli.",
    )
    satuan: Optional[str] = Field(
        default=None,
        alias="Satuan",
        description="Satuan sumber, bukan hasil konversi.",
    )
    halaman_pdf: Optional[int] = Field(
        default=None,
        alias="Halaman PDF",
        ge=1,
        description="Nomor halaman PDF bukti.",
    )


Record = TargetKomitmenIklimRecord
