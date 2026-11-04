# Data Dictionary: Indonesia Energy Balance Table 2025

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Indonesia Energy Balance Table 2025`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [HEESI 2025 - Energy Balance](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=2pMWT6&nav=MTVfezVGRjBBODJELUM5QjctNDZBNS04QURDLTREMzM1M0Y5RUIxNH0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/indonesia_energy_balance_table_2025/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | Tahun | Tahun Energy Balance Table (2025) |
| kategori | `kategori` | String | - | Nama baris neraca energi sesuai tabel sumber: Primary Energy Supply, Production, Import, Export, International Marine Bunker, Stock Change, Energy Transformation, Refinery, Gas Processing, LNG Regasification, Coal Processing Plant, Biofuel Blending, Power Plant, State Own Utility (PLN), IPP Captive Power and PPU (Non-PLN), IUPTLS + PPU, Own Use and Losses, During Transformation, Energy Use/Own Use, Transmission & Distribution, Final Energy Supply, Statistic Discrepancy, Final Consumption, Final Energy Consumption, Industry, Transportation, Household, Commercial, Other Sector, Non Energy Use |
| jenis_energi | `jenis_energi` | String | - | Jenis energi (kolom tabel): Hydro Power, Geothermal, Solar PP & Solar PV, Wind PP, Other Renewables, Industrial Biomass, Solar Water Heater, Direct Use of Geothermal, Traditional Biomass, Coal, Briquette, Natural Gas, Crude Oil, Oil Fuel, Biofuel, Biogas, LPG, Electricity, LNG, Total (Total adalah jumlah seluruh jenis energi pada kategori tersebut; jangan dijumlahkan bersama jenis energi lainnya) |
| nilai | `nilai` | Integer | Ribu BOE | Nilai energi (Thousand BOE). Negatif berarti pengurangan (ekspor, input transformasi, losses); positif berarti penambahan/output |
| satuan | `satuan` | String | - | Satuan nilai: Thousand BOE (BOE = Barrel of Oil Equivalent) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class IndonesiaEnergyBalanceTable2025Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun Energy Balance Table (2025)")
    kategori: str | None = Field(default=None, alias="kategori", description="Nama baris neraca energi sesuai tabel sumber: Primary Energy Supply, Production, Import, Export, International Marine Bunker, Stock Change, Energy Transformation, Refinery, Gas Processing, LNG Regasification, Coal Processing Plant, Biofuel Blending, Power Plant, State Own Utility (PLN), IPP Captive Power and PPU (Non-PLN), IUPTLS + PPU, Own Use and Losses, During Transformation, Energy Use/Own Use, Transmission & Distribution, Final Energy Supply, Statistic Discrepancy, Final Consumption, Final Energy Consumption, Industry, Transportation, Household, Commercial, Other Sector, Non Energy Use")
    jenis_energi: str | None = Field(default=None, alias="jenis_energi", description="Jenis energi (kolom tabel): Hydro Power, Geothermal, Solar PP & Solar PV, Wind PP, Other Renewables, Industrial Biomass, Solar Water Heater, Direct Use of Geothermal, Traditional Biomass, Coal, Briquette, Natural Gas, Crude Oil, Oil Fuel, Biofuel, Biogas, LPG, Electricity, LNG, Total (Total adalah jumlah seluruh jenis energi pada kategori tersebut; jangan dijumlahkan bersama jenis energi lainnya)")
    nilai: int | None = Field(default=None, alias="nilai", description="Nilai energi (Thousand BOE). Negatif berarti pengurangan (ekspor, input transformasi, losses); positif berarti penambahan/output")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai: Thousand BOE (BOE = Barrel of Oil Equivalent)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
