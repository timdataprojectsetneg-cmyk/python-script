"""Pydantic schema — Data Penyalur Non PPN 2025 (mirrors the Data Dictionary)."""

from datetime import date
from pydantic import BaseModel, Field


class Record(BaseModel):
    tanggal_publikasi: date | None = Field(default=None, alias="tanggal_publikasi", description="Tanggal artikel terbit")
    nama_pipa: str | None = Field(default=None, alias="nama_pipa", description="Nama pipa transmisi gas bumi")
    titik_awal: str | None = Field(default=None, alias="titik_awal", description="Titik awal pipa (dari nama pipa)")
    titik_akhir: str | None = Field(default=None, alias="titik_akhir", description="Titik akhir pipa (dari nama pipa)")
    status_pipa: str | None = Field(default=None, alias="status_pipa", description="Status pembangunan sebagaimana disebut artikel")
    sumber: str | None = Field(default=None, alias="sumber", description="Nama sumber dan penyampai")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

