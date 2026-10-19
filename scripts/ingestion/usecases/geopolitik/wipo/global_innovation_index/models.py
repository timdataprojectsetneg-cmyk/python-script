"""Pydantic schema for WIPO Global Innovation Index."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class WipoGlobalInnovationIndexRecord(BaseModel):
    tahun: int = Field(
        description="Tahun pemeringkatan indeks inovasi global (misal: 2026)."
    )
    skor_gii_indonesia: float = Field(
        default=0.0,
        description="Skor komposit Global Innovation Index Indonesia (skala 0-100)."
    )
    peringkat_gii_indonesia: int = Field(
        default=0,
        description="Peringkat inovasi Indonesia di antara 133 ekonomi dunia."
    )
    peringkat_asean: int = Field(
        default=0,
        description="Peringkat inovasi di kawasan ASEAN."
    )
    pilar_institusi: float = Field(
        default=0.0,
        description="Skor pilar kelembagaan institusi (Institutions)."
    )
    pilar_human_capital: float = Field(
        default=0.0,
        description="Skor pilar modal manusia dan riset (Human Capital & Research)."
    )
    pilar_infrastruktur: float = Field(
        default=0.0,
        description="Skor pilar infrastruktur teknologi & inovasi (Infrastructure)."
    )
    pilar_market_sophistication: float = Field(
        default=0.0,
        description="Skor pilar kecanggihan pasar modal & kredit (Market Sophistication)."
    )
    pilar_business_sophistication: float = Field(
        default=0.0,
        description="Skor pilar kecanggihan bisnis & pekerja berbasis pengetahuan (Business Sophistication)."
    )
    pilar_knowledge_technology: float = Field(
        default=0.0,
        description="Skor pilar keluaran pengetahuan & teknologi (Knowledge & Technology Outputs)."
    )
    pilar_creative_outputs: float = Field(
        default=0.0,
        description="Skor pilar luaran kreatif & hak cipta industri (Creative Outputs)."
    )
    data_source: str = Field(
        default="World Intellectual Property Organization (WIPO)",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = WipoGlobalInnovationIndexRecord
