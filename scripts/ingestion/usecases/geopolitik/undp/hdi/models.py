"""Pydantic schema for UNDP Human Development Index (HDI) time series."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UndpHdiRecord(BaseModel):
    tahun: int = Field(
        description="Tahun laporan atau observasi Human Development Index."
    )
    negara: str = Field(
        description="Nama negara (misal: Indonesia, Malaysia, Singapore)."
    )
    iso3: Optional[str] = Field(
        default=None,
        description="Kode 3 huruf ISO3 negara (misal: IDN, MYS, SGP, USA)."
    )
    skor_hdi: float = Field(
        description="Skor komposit Human Development Index (skala 0.000 - 1.000)."
    )
    peringkat_hdi_dunia: Optional[int] = Field(
        default=None,
        description="Peringkat pembangunan manusia global terkini."
    )
    angka_harapan_hidup_tahun: Optional[float] = Field(
        default=None,
        description="Angka Harapan Hidup saat lahir dalam satuan tahun (Life Expectancy)."
    )
    harapan_lama_sekolah_tahun: Optional[float] = Field(
        default=None,
        description="Perkiraan lama sekolah yang diharapkan ditempuh anak usia sekolah (Expected Years of Schooling)."
    )
    rata_rata_lama_sekolah_tahun: Optional[float] = Field(
        default=None,
        description="Rata-rata lama sekolah riil yang dicapai penduduk usia 25 tahun ke atas (Mean Years of Schooling)."
    )
    gni_per_kapita_ppp_usd: Optional[float] = Field(
        default=None,
        description="Pendapatan Nasional Bruto per kapita berbasis Purchasing Power Parity dalam satuan USD (GNI per capita PPP)."
    )
    kategori_hdi: Optional[str] = Field(
        default="High Human Development",
        description="Klasifikasi tingkat pembangunan manusia: Very High (>=0.800), High (0.700-0.799), Medium (0.550-0.699), Low (<0.550)."
    )
    data_source: str = Field(
        default="United Nations Development Programme (UNDP) HDR Time Series",
        description="Sumber data resmi internasional."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = UndpHdiRecord
