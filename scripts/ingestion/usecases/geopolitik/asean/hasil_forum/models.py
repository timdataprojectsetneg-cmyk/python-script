"""Pydantic schema for Hasil Forum ASEAN (Chairman's Statement, one row per paragraph)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HasilForumRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    tanggal_forum: Optional[date] = Field(
        default=None,
        alias="Tanggal Forum",
        description="Tanggal forum/KTT sebagaimana tercantum pada judul dokumen.",
    )
    forum: Optional[str] = Field(
        default=None,
        alias="Forum",
        description="Judul pernyataan/forum penerbit (mis. Chairman's Statement of the 46th ASEAN Summit).",
    )
    paragraf: Optional[int] = Field(
        default=None,
        alias="Paragraf",
        ge=1,
        description="Nomor paragraf dokumen sumber.",
    )
    isu: Optional[str] = Field(
        default=None,
        alias="Isu",
        description="Judul bagian (heading) dokumen yang memuat paragraf; kosong untuk paragraf pembuka.",
    )
    hasil_sikap_bersama: Optional[str] = Field(
        default=None,
        alias="Hasil/Sikap Bersama",
        description="Teks paragraf apa adanya dari dokumen (bukan parafrasa).",
    )


Record = HasilForumRecord
