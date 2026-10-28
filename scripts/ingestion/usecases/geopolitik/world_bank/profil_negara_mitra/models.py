"""Pydantic schema mirroring dictionary_profil_negara_mitra.md."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProfilNegaraMitraRecord(BaseModel):
    id: str = Field(description="Kode ekonomi/negara World Bank (ISO3 atau kode agregat).")
    name: Optional[str] = Field(default=None, description="Nama negara/ekonomi sumber.")
    capitalcity: Optional[str] = Field(
        default=None, alias="capitalCity", description="Nama ibu kota menurut metadata sumber."
    )
    region: Optional[str] = Field(default=None, description="Kelompok kawasan World Bank.")
    incomelevel: Optional[str] = Field(
        default=None, alias="incomeLevel", description="Kelompok pendapatan World Bank."
    )
    latitude: Optional[float] = Field(default=None, description="Lintang ibu kota (derajat).")
    longitude: Optional[float] = Field(default=None, description="Bujur ibu kota (derajat).")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


Record = ProfilNegaraMitraRecord
