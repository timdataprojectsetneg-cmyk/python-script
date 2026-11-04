# Data Dictionary: 3.2.2 Energy Consumption (Excluded Traditional Biomass)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `3.2.2 Energy Consumption (Excluded Traditional Biomass)`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [HEESI 2025 - Energy Consumption](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=67Bq42&nav=MTVfezkxNjI5QkQzLTUxQTktNDQ5Ri1BOEU2LTUxQ0UwNDc0NkRGQn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/energy_consumption/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| year | `year` | Integer | Tahun | Tahun data konsumsi energi (2015-2025) |
| sector | `sector` | String | - | Nama sektor atau baris agregat sesuai tabel sumber: Industrial, Households, Commercial, Transportation, Other, Final Energy Consumption, Non Energy Utilization |
| category | `category` | String | - | Klasifikasi baris: sector (sektor pengguna akhir), total (Final Energy Consumption), non_energy (Non Energy Utilization) |
| value | `value` | Integer | Ribu BOE | Nilai konsumsi energi (Thousand BOE), tidak termasuk biomassa tradisional |
| revised | `revised` | Boolean | - | Penanda data revisi sesuai catatan 1) pada dokumen (true untuk 2020-2024, false untuk lainnya) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class EnergyConsumptionRecord(BaseModel):
    year: int | None = Field(default=None, alias="year", description="Tahun data konsumsi energi (2015-2025)")
    sector: str | None = Field(default=None, alias="sector", description="Nama sektor atau baris agregat sesuai tabel sumber: Industrial, Households, Commercial, Transportation, Other, Final Energy Consumption, Non Energy Utilization")
    category: str | None = Field(default=None, alias="category", description="Klasifikasi baris: sector (sektor pengguna akhir), total (Final Energy Consumption), non_energy (Non Energy Utilization)")
    value: int | None = Field(default=None, alias="value", description="Nilai konsumsi energi (Thousand BOE), tidak termasuk biomassa tradisional")
    revised: bool | None = Field(default=None, alias="revised", description="Penanda data revisi sesuai catatan 1) pada dokumen (true untuk 2020-2024, false untuk lainnya)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
