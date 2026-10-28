"""Pydantic schema for Keanggotaan Forum (World Bank Group)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KeanggotaanForumRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    organisasi_forum: Optional[str] = Field(
        default=None,
        alias="Organisasi/Forum",
        description="Nama organisasi anggota World Bank Group (IBRD, IDA, IFC, MIGA, ICSID).",
    )
    status_peran: Optional[str] = Field(
        default=None,
        alias="Status/Peran",
        description="Status yang disebut dalam sumber primer (Member).",
    )
    tanggal_tahun_periode: Optional[str] = Field(
        default=None,
        alias="Tanggal/Tahun/Periode",
        description="Tanggal masuk (ISO YYYY-MM-DD) sebagaimana daftar anggota World Bank.",
    )
    keterangan_periode: Optional[str] = Field(
        default=None,
        alias="Keterangan Periode",
        description="Makna tanggal: tanggal keanggotaan (Date of Membership) pada daftar resmi.",
    )
    url_sumber: Optional[str] = Field(
        default=None,
        alias="URL Sumber",
        description="Halaman daftar anggota World Bank Group.",
    )
    negara: Optional[str] = Field(
        default=None,
        alias="Negara",
        description="Negara anggota yang disaring dari daftar (default Indonesia).",
    )


Record = KeanggotaanForumRecord
