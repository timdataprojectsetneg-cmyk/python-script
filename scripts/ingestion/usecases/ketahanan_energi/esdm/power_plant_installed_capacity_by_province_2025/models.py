"""Pydantic schema — 6.4.9 Power Plant Installed Capacity by Province 2025 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data kapasitas terpasang pembangkit (2025)")
    kategori: str | None = Field(default=None, alias="kategori", description="Jenis pembangkit: Hydro PP, Mini Hydro PP, Micro Hydro PP, Geothermal PP, Solar PP, Wind PP, Biogas PP, Biomass PP, Biofuel PP, Waste PP, Diesel PP, Steam PP, Gas PP, Coal Gasification PP, Combined Gas-Steam PP, Gas Engine PP, Other PP, Total (jumlah seluruh jenis pembangkit di provinsi tersebut)")
    nilai: float | None = Field(default=None, alias="nilai", description="Kapasitas terpasang pembangkit listrik (megawatt); tanda \"-\" pada sumber ditulis 0")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai, yaitu MW (megawatt)")

    provinsi: str | None = Field(default=None, alias="provinsi", description="Nama provinsi sesuai tabel sumber (38 provinsi)")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
