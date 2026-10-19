"""Pydantic schema for GDELT Media Asing."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GdeltMediaAsingRecord(BaseModel):
    tanggal_artikel: Optional[str] = Field(
        default=None,
        description="Waktu publikasi berita internasional (format YYYY-MM-DD)."
    )
    judul_berita: str = Field(
        description="Judul artikel berita media asing tentang Indonesia."
    )
    nama_media_sumber: str = Field(
        description="Nama kantor berita / media asing (Reuters, Bloomberg, Nikkei Asia, dll.)."
    )
    negara_asal_media: Optional[str] = Field(
        default=None,
        description="Negara basis media penerbit."
    )
    kawasan_media: Optional[str] = Field(
        default=None,
        description="Kawasan asal media (Asia Pasifik, Amerika Utara, Eropa)."
    )
    topik_utama: str = Field(
        default="Diplomasi & Geopolitik",
        description="Kategori isu (Diplomasi & Geopolitik, Investasi & Nikel, Hankam)."
    )
    skor_sentimen_gdelt: float = Field(
        default=0.0,
        description="Skor tone sentimen algoritma GDELT (-10.0 s.d +10.0)."
    )
    url_artikel: Optional[str] = Field(
        default=None,
        description="Tautan URL artikel berita daring asli."
    )
    data_source: str = Field(
        default="GDELT Project 2.0 (Global Database of Events, Language, and Tone)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = GdeltMediaAsingRecord
