# Data Dictionary: Primary Energy Supply

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Primary Energy Supply`
- Publisher: esdm
- Data access: `pdf`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Primary Energy Supply (Million BOE) and Share of Primary Energy Supply (%) in 2025](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=wDK3Yt&nav=MTVfezQ0N0VFNzJELTcwREQtNDFGMC04QUY5LURGNjMxQzNFNzgyM30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/primary_energy_supply/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun pasokan energi primer (grafik 2019–2025) |
| jenis_energi | `jenis_energi` | Categorical | - | Crude Oil & Product, Natural Gas & Product, Coal, NRE (New and Renewable Energy), atau Total |
| pasokan | `pasokan` | Numeric (Decimal) | Million BOE | Pasokan energi primer per jenis energi |
| pangsa_persen | `pangsa_persen` | Numeric (Decimal) | % | Porsi terhadap total pasokan energi primer tahun tersebut (diagram donat) |
| pertumbuhan_yoy_persen | `pertumbuhan_yoy_persen` | Numeric (Decimal) | % | Pertumbuhan dibanding tahun sebelumnya, dari teks ringkasan |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PrimaryEnergySupplyRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun pasokan energi primer (grafik 2019–2025)")
    jenis_energi: str | None = Field(default=None, alias="jenis_energi", description="Crude Oil & Product, Natural Gas & Product, Coal, NRE (New and Renewable Energy), atau Total")
    pasokan: str | None = Field(default=None, alias="pasokan", description="Pasokan energi primer per jenis energi")
    pangsa_persen: str | None = Field(default=None, alias="pangsa_persen", description="Porsi terhadap total pasokan energi primer tahun tersebut (diagram donat)")
    pertumbuhan_yoy_persen: str | None = Field(default=None, alias="pertumbuhan_yoy_persen", description="Pertumbuhan dibanding tahun sebelumnya, dari teks ringkasan")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
