"""Pydantic schema mirroring the Data Dictionary for Ekspor HS Pertanian."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EksporHsPertanianRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    tahun: int = Field(alias="Tahun", description="Tahun observasi.")
    arus: str = Field(alias="Arus", description="Arah perdagangan.")
    subsektor: str = Field(alias="Subsektor", description="Subsektor yang dipilih pada query.")
    kelompok_komoditas: Optional[str] = Field(
        default=None, alias="Kelompok Komoditas", description="Kelompok komoditas pada tabel sumber."
    )
    kode_hs: str = Field(
        alias="Kode HS",
        description="Kode Harmonized System; disimpan sebagai teks agar nol awal tidak hilang.",
    )
    deskripsi_hs: Optional[str] = Field(default=None, alias="Deskripsi HS", description="Deskripsi barang pada portal.")
    nomor_bulan: int = Field(alias="Nomor Bulan", description="Nomor 1-12 untuk pengurutan.")
    bulan: str = Field(alias="Bulan", description="Nama bulan dalam Bahasa Indonesia.")
    volume: Optional[float] = Field(default=None, alias="Volume", description="Volume perdagangan bulan tersebut (Kg).")
    nilai: Optional[float] = Field(default=None, alias="Nilai", description="Nilai perdagangan bulan tersebut (USD).")


Record = EksporHsPertanianRecord
