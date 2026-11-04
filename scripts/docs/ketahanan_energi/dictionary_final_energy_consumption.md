# Data Dictionary: Final Energy Consumption

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Final Energy Consumption`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_ES Final Energy Consumption](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=ETJpiJ&nav=MTVfezM5QjE3NUE5LUYzRjktNDVCMi05NEMyLTMyRDREMzU4RDBGQ30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/final_energy_consumption/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun konsumsi energi final (grafik 2019–2025) |
| sektor | `sektor` | Categorical | - | Industry, Household, Commercial, Transportation, Others, atau Total |
| konsumsi | `konsumsi` | Numeric (Decimal) | Million BOE | Konsumsi energi final per sektor |
| pangsa_persen | `pangsa_persen` | Numeric (Decimal) | % | Porsi terhadap total konsumsi energi final (diagram donat) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class FinalEnergyConsumptionRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun konsumsi energi final (grafik 2019–2025)")
    sektor: str | None = Field(default=None, alias="sektor", description="Industry, Household, Commercial, Transportation, Others, atau Total")
    konsumsi: str | None = Field(default=None, alias="konsumsi", description="Konsumsi energi final per sektor")
    pangsa_persen: str | None = Field(default=None, alias="pangsa_persen", description="Porsi terhadap total konsumsi energi final (diagram donat)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
