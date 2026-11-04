# Data Dictionary: 3.3 Final Energy Consumption by Type

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `3.3 Final Energy Consumption by Type`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Final Energy Consumption by Type](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=M4pylU&nav=MTVfezZBNjdFRUM5LTBEOTUtNDIzOS1BN0JBLTVFNzAzMDJGMkVCNn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/final_energy_consumption_by_type/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Year | `year` | Integer | Tahun | Tahun/periode data pada tabel konsumsi energi final per sektor. |
| Sector | `sector` | Categorical | - | Sektor pengguna energi: Industrial, Households, Commercial, Transportation, Other, Final Energy Consumption (total), dan Non Energy Utilization. |
| Energy Consumption | `energy_consumption` | Numeric | Belum terlihat* | Jumlah konsumsi energi pada sektor dan tahun tersebut. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class FinalEnergyConsumptionByTypeRecord(BaseModel):
    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data pada tabel konsumsi energi final per sektor.")
    sector: str | None = Field(default=None, alias="Sector", description="Sektor pengguna energi: Industrial, Households, Commercial, Transportation, Other, Final Energy Consumption (total), dan Non Energy Utilization.")
    energy_consumption: str | None = Field(default=None, alias="Energy Consumption", description="Jumlah konsumsi energi pada sektor dan tahun tersebut.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
