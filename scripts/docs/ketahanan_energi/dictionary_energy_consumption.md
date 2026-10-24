# Data Dictionary: HANDBOOK OF ENERGY & ECONOMIC STATISTICS OF INDONESIA 2025 - 3.2.2 Energy Consumption (Excluded Traditional Biomass)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `HANDBOOK OF ENERGY & ECONOMIC STATISTICS OF INDONESIA 2025 - 3.2.2 Energy Consumption (Excluded Traditional Biomass)`
- Publisher: esdm
- Data access: `pdf`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [HEESI 2025 - Energy Consumption](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=67Bq42&nav=MTVfezkxNjI5QkQzLTUxQTktNDQ5Ri1BOEU2LTUxQ0UwNDc0NkRGQn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/energy_consumption/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | Integer | Tahun | Tahun buku laporan keuangan |
| Komponen Biaya | `komponen_biaya` | String | - | Pos biaya pada cost of sales PGN |
| Jenis Biaya | `jenis_biaya` | Categorical | - | Raw material, service, labor, depreciation, maintenance, fuel, overhead |
| Nilai | `nilai` | Decimal | USD | Nilai komponen biaya sesuai laporan keuangan |
| Tahun Pembanding | `tahun_pembanding` | Integer | Tahun | Tahun 2024 sebagai comparative figure |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class EnergyConsumptionRecord(BaseModel):
    periode: int | None = Field(default=None, alias="Periode", description="Tahun buku laporan keuangan")
    komponen_biaya: str | None = Field(default=None, alias="Komponen Biaya", description="Pos biaya pada cost of sales PGN")
    jenis_biaya: str | None = Field(default=None, alias="Jenis Biaya", description="Raw material, service, labor, depreciation, maintenance, fuel, overhead")
    nilai: float | None = Field(default=None, alias="Nilai", description="Nilai komponen biaya sesuai laporan keuangan")
    tahun_pembanding: int | None = Field(default=None, alias="Tahun Pembanding", description="Tahun 2024 sebagai comparative figure")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
