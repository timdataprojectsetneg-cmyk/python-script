"""Pydantic schema mirroring the Data Dictionary for Ekspor Impor Bulanan BPS."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EksporImporBulananBpsRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    periode: str = Field(alias="Periode", description="Bulan observasi perdagangan (YYYY-MM).")
    nilai_ekspor: Optional[float] = Field(
        default=None, alias="Nilai Ekspor", description="Nilai ekspor barang Indonesia pada bulan observasi (USD)."
    )
    berat_ekspor: Optional[float] = Field(
        default=None, alias="Berat Ekspor", description="Berat bersih ekspor barang pada bulan observasi (Kg)."
    )
    nilai_impor: Optional[float] = Field(
        default=None, alias="Nilai Impor", description="Nilai impor barang Indonesia pada bulan observasi (USD)."
    )
    berat_impor: Optional[float] = Field(
        default=None, alias="Berat Impor", description="Berat bersih impor barang pada bulan observasi (Kg)."
    )


Record = EksporImporBulananBpsRecord
