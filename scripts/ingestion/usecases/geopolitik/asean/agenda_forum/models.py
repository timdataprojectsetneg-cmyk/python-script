"""Pydantic schema for Agenda Forum ASEAN (ASEAN Notional Calendar)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AgendaForumRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    nomor_pada_kalender: Optional[int] = Field(
        default=None,
        alias="Nomor pada Kalender",
        ge=1,
        description="Nomor kegiatan asli untuk menemukan record.",
    )
    pertemuan: Optional[str] = Field(
        default=None,
        alias="Pertemuan",
        description="Nama kegiatan sebagaimana kalender.",
    )
    jadwal_menurut_sumber: Optional[str] = Field(
        default=None,
        alias="Jadwal menurut Sumber",
        description="Rentang/jadwal indikatif apa adanya (mis. 10-11 December 2025 (TBC), Q4); tidak dipaksakan menjadi tanggal pasti.",
    )
    lokasi_menurut_sumber: Optional[str] = Field(
        default=None,
        alias="Lokasi menurut Sumber",
        description="Lokasi atau TBC (to be confirmed); kosong bila sumber tidak mencantumkan.",
    )
    pilar: Optional[str] = Field(
        default=None,
        alias="Pilar",
        description="AEC = ekonomi; APSC = politik-keamanan; ASCC = sosial-budaya; Cross-Pillar bila lintas pilar.",
    )


Record = AgendaForumRecord
