"""Pydantic schema — 3.2.2 Energy Consumption (Excluded Traditional Biomass) (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):

    year: int | None = Field(default=None, alias="year", description="Tahun data konsumsi energi (2015-2025)")
    sector: str | None = Field(default=None, alias="sector", description="Nama sektor atau baris agregat sesuai tabel sumber: Industrial, Households, Commercial, Transportation, Other, Final Energy Consumption, Non Energy Utilization")
    category: str | None = Field(default=None, alias="category", description="Klasifikasi baris: sector (sektor pengguna akhir), total (Final Energy Consumption), non_energy (Non Energy Utilization)")
    value: int | None = Field(default=None, alias="value", description="Nilai konsumsi energi (Thousand BOE), tidak termasuk biomassa tradisional")
    revised: bool | None = Field(default=None, alias="revised", description="Penanda data revisi sesuai catatan 1) pada dokumen (true untuk 2020-2024, false untuk lainnya)")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
