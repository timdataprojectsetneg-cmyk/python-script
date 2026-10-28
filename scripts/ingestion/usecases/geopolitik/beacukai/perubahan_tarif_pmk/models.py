"""Pydantic schema mirroring the Data Dictionary for Perubahan Tarif PMK 50-2026."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PerubahanTarifPmkRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    peraturan: Optional[str] = Field(
        default=None, alias="Peraturan", description="Nomor regulasi yang menjadi dasar perubahan tarif."
    )
    tanggal_berlaku: Optional[date] = Field(
        default=None, alias="Tanggal Berlaku", description="Tanggal mulai berlaku regulasi."
    )
    kode_hs: Optional[str] = Field(
        default=None, alias="Kode HS", description="Pos tarif (HS) yang tarifnya berubah: Pasal II dan setiap baris Lampiran III yang bukan 'Tetap'."
    )
    komoditas: Optional[str] = Field(
        default=None, alias="Komoditas", description="Uraian barang baris Lampiran III; untuk pos tarif Pasal II tanpa baris tabel, kelompok barang Pasal II."
    )
    tarif_bea_masuk: Optional[float] = Field(
        default=None,
        alias="Tarif Bea Masuk",
        ge=0,
        description="Tarif bea masuk (persen) pada baris Lampiran III; tarif Pasal II bila baris tidak mencantumkannya.",
    )
    masa_berlaku_tarif: Optional[str] = Field(
        default=None, alias="Masa Berlaku Tarif", description="Durasi khusus Pasal II (hanya untuk pos tarif Pasal II)."
    )
    konteks_kebijakan: Optional[str] = Field(
        default=None,
        alias="Konteks Kebijakan",
        description="Tujuan kebijakan yang dijelaskan dalam pertimbangan regulasi.",
    )
    halaman_pdf: Optional[int] = Field(
        default=None, alias="Halaman PDF", description="Halaman bukti dalam PDF resmi."
    )


Record = PerubahanTarifPmkRecord
