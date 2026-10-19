"""Pydantic schema for GDELT Sentimen Wilayah Program Prioritas."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GdeltSentimenWilayahRecord(BaseModel):
    tanggal_pemantauan: Optional[str] = Field(
        default=None,
        description="Waktu monitoring percakapan publik (format YYYY-MM-DD)."
    )
    nama_program_prioritas: str = Field(
        description="Nama program prioritas (Makan Bergizi Gratis (MBG), Koperasi Desa Merah Putih, Penurunan Stunting, Cek Kesehatan Gratis (CKG), PSN)."
    )
    provinsi_wilayah: str = Field(
        description="Provinsi sasaran pemantauan isu (Jawa Tengah, Jawa Barat, Jawa Timur, dll.)."
    )
    volume_percakapan_media: int = Field(
        default=0,
        description="Jumlah mention dan artikel yang beredar di ruang publik."
    )
    sentimen_positif_pct: float = Field(
        default=0.0,
        description="Proporsi sentimen positif publik (%)"
    )
    sentimen_netral_pct: float = Field(
        default=0.0,
        description="Proporsi sentimen netral publik (%)"
    )
    sentimen_negatif_pct: float = Field(
        default=0.0,
        description="Proporsi sentimen kritis / negatif publik (%)"
    )
    isu_dominan_diperbincangkan: Optional[str] = Field(
        default=None,
        description="Substansi narasi utama di ruang publik lokal."
    )
    kanal_utama_sumber: Optional[str] = Field(
        default=None,
        description="Kanal percakapan terbanyak (Media Daring, X/Twitter, Instagram, Portal Berita)."
    )
    data_source: str = Field(
        default="GDELT Project 2.0 & Media Monitoring Nasional",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = GdeltSentimenWilayahRecord
