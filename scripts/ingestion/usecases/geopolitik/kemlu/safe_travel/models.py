"""Pydantic schema mirroring the Data Dictionary for Kemlu Safe Travel Appeals."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SafeTravelRecord(BaseModel):
    negara: str = Field(
        default="Global / Semua Negara",
        description="Negara tujuan perjalanan yang menjadi sasaran imbauan resmi."
    )
    kawasan: Optional[str] = Field(
        default="Global",
        description="Kawasan geografis negara tujuan (misal: Asia Tenggara, Timur Tengah, Eropa)."
    )
    level_peringatan: str = Field(
        default="Level 1 - Aman (Hijau)",
        description="Tingkat keamanan: Level 1 Aman, Level 2 Waspada, Level 3 Hati-hati, Level 4 Bahaya."
    )
    ringkasan_imbauan: str = Field(
        description="Substansi imbauan resmi bagi WNI."
    )
    tanggal_rilis: str = Field(
        description="Waktu publikasi imbauan (format ISO YYYY-MM-DD)."
    )
    pemicu_peringatan: str = Field(
        default="Informasi Umum & Regulasi",
        description="Penyebab eskalasi risiko (Konflik Bersenjata, Bencana Alam, Kerusuhan, Wabah, Regulasi)."
    )
    nomor_hotline_kbri_kjri: Optional[str] = Field(
        default=None,
        description="Nomor hotline darurat perwakilan RI setempat (KBRI/KJRI)."
    )
    news_id: Optional[str] = Field(
        default=None,
        description="ID unik berita imbauan dari portal Safe Travel."
    )
    uuid: Optional[str] = Field(
        default=None,
        description="UUID record Safe Travel Kemlu."
    )
    news_title: Optional[str] = Field(
        default=None,
        description="Judul lengkap siaran imbauan perjalanan."
    )
    news_info: Optional[str] = Field(
        default=None,
        description="Kategori informasi internal Kemlu (Keamanan, Keimigrasian, Kesehatan, dsb)."
    )
    news_image_path: Optional[str] = Field(
        default=None,
        description="Tautan gambar atau poster imbauan resmi."
    )
    news_total_read: Optional[int] = Field(
        default=0,
        description="Jumlah pembaca siaran imbauan."
    )
    data_source: str = Field(
        default="Kementerian Luar Negeri RI - Portal Safe Travel",
        description="Sumber data resmi penyedia imbauan."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = SafeTravelRecord
