# Data Dictionary: 6.2.9 LPG Supply and Demand

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `6.2.9 LPG Supply and Demand`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_LPG Supply and Demand](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=WnPPUh&nav=MTVfe0RFQjczMkY3LThDRDctNDdBMS05MDU1LUM5MDU1OUE3QUFFQn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/lpg_supply_and_demand/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| kategori | `kategori` | Categorical | - | Komponen neraca LPG, mis. Production - Gas Refinery, Production - Oil Refinery, Production - Total, Export, Import, Sales |
| nilai | `nilai` | Numeric (Decimal) | Ton | Volume LPG per kategori dan tahun |
| satuan | `satuan` | Categorical | - | Ton |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class LpgSupplyAndDemandRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Komponen neraca LPG, mis. Production - Gas Refinery, Production - Oil Refinery, Production - Total, Export, Import, Sales")
    nilai: str | None = Field(default=None, alias="nilai", description="Volume LPG per kategori dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="Ton")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
