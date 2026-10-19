"""Pydantic schema for UN Voting Sidang PBB."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UnVotingSidangPbbRecord(BaseModel):
    nomor_resolusi: str = Field(
        description="Nomor dokumen resolusi PBB (misal: 'A/RES/79/112')."
    )
    badan_pbb: str = Field(
        default="UN General Assembly",
        description="Badan pelaksana pemungutan suara (UN General Assembly / UN Security Council)."
    )
    tanggal_voting: Optional[str] = Field(
        default=None,
        description="Waktu pemungutan suara berlangsung (format YYYY-MM-DD)."
    )
    judul_resolusi: str = Field(
        description="Substansi isu yang diputuskan dalam resolusi PBB."
    )
    posisi_indonesia: str = Field(
        default="In Favor",
        description="Sikap suara RI (In Favor / Setuju, Against / Menolak, Abstain)."
    )
    total_suara_in_favor: int = Field(
        default=0,
        description="Jumlah total negara anggota yang mendukung resolusi."
    )
    total_suara_against: int = Field(
        default=0,
        description="Jumlah total negara anggota yang menolak resolusi."
    )
    total_abstain: int = Field(
        default=0,
        description="Jumlah total negara anggota yang menyatakan abstain."
    )
    posisi_negara_mitra_utama: Optional[str] = Field(
        default=None,
        description="Perbandingan sikap suara negara mitra strategis (ASEAN, AS, Tiongkok, dll.)."
    )
    data_source: str = Field(
        default="United Nations Digital Library & PTRI New York",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = UnVotingSidangPbbRecord
