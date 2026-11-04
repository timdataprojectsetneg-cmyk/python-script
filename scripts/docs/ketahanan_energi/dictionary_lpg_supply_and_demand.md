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
| Year | `year` | Integer | Tahun | Tahun/periode data |
| Production Gas Refinery (Ton) | `production_gas_refinery_ton` | Numeric | Ton | Produksi LPG dari kilang gas |
| Production Oil Refinery (Ton) | `production_oil_refinery_ton` | Numeric | Ton | Produksi LPG dari kilang minyak |
| Production Total (Ton) | `production_total_ton` | Numeric | Ton | Total produksi LPG dalam negeri |
| Export (Ton) | `export_ton` | Numeric | Ton | Jumlah LPG yang diekspor |
| Import (Ton) | `import_ton` | Numeric | Ton | Jumlah LPG yang diimpor |
| Sales (Ton) | `sales_ton` | Numeric | Ton | Penjualan LPG (termasuk refrigerant) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class LpgSupplyAndDemandRecord(BaseModel):
    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data")
    production_gas_refinery_ton: str | None = Field(default=None, alias="Production Gas Refinery (Ton)", description="Produksi LPG dari kilang gas")
    production_oil_refinery_ton: str | None = Field(default=None, alias="Production Oil Refinery (Ton)", description="Produksi LPG dari kilang minyak")
    production_total_ton: str | None = Field(default=None, alias="Production Total (Ton)", description="Total produksi LPG dalam negeri")
    export_ton: str | None = Field(default=None, alias="Export (Ton)", description="Jumlah LPG yang diekspor")
    import_ton: str | None = Field(default=None, alias="Import (Ton)", description="Jumlah LPG yang diimpor")
    sales_ton: str | None = Field(default=None, alias="Sales (Ton)", description="Penjualan LPG (termasuk refrigerant)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
