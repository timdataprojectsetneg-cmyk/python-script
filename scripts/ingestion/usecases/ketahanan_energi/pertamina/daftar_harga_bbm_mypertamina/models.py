"""Pydantic schema — Daftar Harga BBM - MyPertamina (mirrors the Data Dictionary)."""
from decimal import Decimal

from datetime import date as DateType
from pydantic import BaseModel, Field


class Record(BaseModel):
    tanggal_berlaku: DateType | None = Field(default=None, alias="Tanggal Berlaku", description="Tanggal mulai berlakunya harga.")
    wilayah: str | None = Field(default=None, alias="Wilayah", description="Provinsi tempat harga berlaku.")
    jenis_bbm: str | None = Field(default=None, alias="Jenis BBM", description="Jenis produk BBM.")
    harga: Decimal | None = Field(default=None, alias="Harga", description="Harga jual eceran per liter.")
    harga_periode_sebelumnya: Decimal | None = Field(default=None, alias="Harga Periode Sebelumnya", description="Harga periode sebelumnya untuk membandingkan perubahan. Tidak tersedia langsung pada halaman saat ini.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
