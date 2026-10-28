"""Pydantic schema mirroring the Data Dictionary for Ekspor Sektor Kemendag."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EksporSektorKemendagRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    periode: Optional[str] = Field(default=None, alias="Periode", description="Bulan observasi (YYYY-MM).")
    total_ekspor: Optional[float] = Field(
        default=None, alias="Total Ekspor", description="Total ekspor migas dan nonmigas (Juta USD)."
    )
    migas: Optional[float] = Field(default=None, alias="Migas", description="Ekspor minyak dan gas bumi (Juta USD).")
    nonmigas: Optional[float] = Field(default=None, alias="Nonmigas", description="Ekspor di luar migas (Juta USD).")
    pertanian: Optional[float] = Field(
        default=None, alias="Pertanian", description="Agriculture: pertanian, perikanan, peternakan dan kehutanan."
    )
    industri: Optional[float] = Field(
        default=None, alias="Industri", description="Industri pengolahan menurut definisi sumber."
    )
    pertambangan: Optional[float] = Field(
        default=None, alias="Pertambangan", description="Batu bara, bijih logam dan tambang lainnya."
    )
    lainnya: Optional[float] = Field(
        default=None, alias="Lainnya", description="Nonmigas di luar pertanian, industri dan pertambangan."
    )


Record = EksporSektorKemendagRecord
