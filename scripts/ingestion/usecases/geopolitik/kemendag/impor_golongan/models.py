"""Pydantic schema mirroring the Data Dictionary for Impor Golongan Kemendag."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ImporGolonganKemendagRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    periode: Optional[str] = Field(default=None, alias="Periode", description="Bulan observasi (YYYY-MM).")
    total_impor: Optional[float] = Field(
        default=None, alias="Total Impor", description="Total impor Indonesia (Juta USD)."
    )
    barang_konsumsi: Optional[float] = Field(
        default=None,
        alias="Barang Konsumsi",
        description="Barang tahan lama/tidak tahan lama untuk konsumsi rumah tangga.",
    )
    bahan_baku_penolong: Optional[float] = Field(
        default=None,
        alias="Bahan Baku/Penolong",
        description="Input dan perlengkapan yang menunjang proses produksi.",
    )
    barang_modal: Optional[float] = Field(
        default=None,
        alias="Barang Modal",
        description="Barang tahan lama untuk kelancaran dan kelangsungan produksi.",
    )


Record = ImporGolonganKemendagRecord
