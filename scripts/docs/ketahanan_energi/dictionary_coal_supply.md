# Data Dictionary: 6.1.2 Coal Supply

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `6.1.2 Coal Supply`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Coal Supply](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=i1F9Rx&nav=MTVfezBFNDc4MTk1LUI5MTQtNDUwMC05MTZFLTA1NkNFNjRBODkzNn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/coal_supply/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Year | `year` | Integer | Tahun | Tahun/periode data pada tabel |
| Production Steam Coal (Ton) | `production_steam_coal_ton` | Numeric | Ton | Jumlah produksi steam coal. |
| Export (Ton) | `export_ton` | Numeric | Ton | Jumlah ekspor komoditas/produk. |
| Import (Ton) | `import_ton` | Numeric | Ton | Jumlah impor komoditas/produk. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class CoalSupplyRecord(BaseModel):
    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data pada tabel")
    production_steam_coal_ton: str | None = Field(default=None, alias="Production Steam Coal (Ton)", description="Jumlah produksi steam coal.")
    export_ton: str | None = Field(default=None, alias="Export (Ton)", description="Jumlah ekspor komoditas/produk.")
    import_ton: str | None = Field(default=None, alias="Import (Ton)", description="Jumlah impor komoditas/produk.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
