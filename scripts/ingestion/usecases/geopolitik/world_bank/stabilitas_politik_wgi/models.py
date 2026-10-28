"""Pydantic schema based on dictionary_stabilitas_politik_wgi.md.

The source file is wide (one column per year); records are emitted long
(one row per country-year) so they load into a flat table.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StabilitasPolitikWgiRecord(BaseModel):
    country_name: str = Field(
        alias="Country Name", description="Nama negara/ekonomi (bahasa Inggris, mis. 'Iran, Islamic Rep.')."
    )
    country_code: str = Field(
        alias="Country Code", description="Kode ISO 3166-1 alpha-3 World Bank. Kunci join ke ref_negara."
    )
    indicator_name: Optional[str] = Field(
        default=None, alias="Indicator Name", description="Nama indikator WGI (konstan untuk satu file)."
    )
    indicator_code: str = Field(alias="Indicator Code", description="Kode indikator, mis. GOV_WGI_PV.EST.")
    year: int = Field(description="Tahun skor. WGI mulai 1996; dua tahunan sebelum 2002.")
    value: float = Field(
        description="Skor stabilitas politik & tidak adanya kekerasan/terorisme (-2,5 s.d. +2,5); makin tinggi makin stabil."
    )
    region: Optional[str] = Field(
        default=None, alias="Region", description="Kawasan World Bank dari Metadata_Country."
    )
    income_group: Optional[str] = Field(
        default=None, alias="IncomeGroup", description="Kelompok pendapatan dari Metadata_Country."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


Record = StabilitasPolitikWgiRecord
