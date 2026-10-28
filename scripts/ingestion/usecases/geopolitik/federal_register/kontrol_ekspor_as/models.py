"""Pydantic schema for Kontrol Ekspor AS (BIS rules published in the Federal Register)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KontrolEksporAsRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    title: Optional[str] = Field(
        default=None, alias="title", description="Judul aturan di Federal Register, mis. \"Revisions to the Entity List\"."
    )
    publication_date: Optional[date] = Field(
        default=None, alias="publication_date", description="Tanggal terbit di Federal Register."
    )
    effective_on: Optional[date] = Field(
        default=None, alias="effective_on", description="Tanggal aturan mulai berlaku (bisa null/berlaku surut)."
    )
    html_url: Optional[str] = Field(default=None, alias="html_url", description="Tautan halaman dokumen.")
    document_number: str = Field(
        alias="document_number*", description="Turunan dari html_url. Kunci dedup; awalan C1- = dokumen koreksi."
    )
    is_correction: bool = Field(
        alias="is_correction*", description="Turunan: True bila document_number berawalan C1-."
    )


Record = KontrolEksporAsRecord
