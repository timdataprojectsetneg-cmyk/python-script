"""Pydantic schema — Indonesia Energy Balance Table 2025 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    nilai: int | None = Field(default=None, alias="nilai", description="Nilai energi (Thousand BOE). Negatif berarti pengurangan (ekspor, input transformasi, losses); positif berarti penambahan/output")

    tahun: int | None = Field(default=None, alias="tahun", description="Tahun Energy Balance Table (2025)")
    kategori: str | None = Field(default=None, alias="kategori", description="Nama baris neraca energi sesuai tabel sumber: Primary Energy Supply, Production, Import, Export, International Marine Bunker, Stock Change, Energy Transformation, Refinery, Gas Processing, LNG Regasification, Coal Processing Plant, Biofuel Blending, Power Plant, State Own Utility (PLN), IPP Captive Power and PPU (Non-PLN), IUPTLS + PPU, Own Use and Losses, During Transformation, Energy Use/Own Use, Transmission & Distribution, Final Energy Supply, Statistic Discrepancy, Final Consumption, Final Energy Consumption, Industry, Transportation, Household, Commercial, Other Sector, Non Energy Use")
    jenis_energi: str | None = Field(default=None, alias="jenis_energi", description="Jenis energi (kolom tabel): Hydro Power, Geothermal, Solar PP & Solar PV, Wind PP, Other Renewables, Industrial Biomass, Solar Water Heater, Direct Use of Geothermal, Traditional Biomass, Coal, Briquette, Natural Gas, Crude Oil, Oil Fuel, Biofuel, Biogas, LPG, Electricity, LNG, Total (Total adalah jumlah seluruh jenis energi pada kategori tersebut; jangan dijumlahkan bersama jenis energi lainnya)")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai: Thousand BOE (BOE = Barrel of Oil Equivalent)")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
