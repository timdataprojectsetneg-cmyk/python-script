# Data Dictionary: Crude Oil and Products

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Crude Oil and Products`
- Publisher: esdm
- Data access: `pdf`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_ES Crude Oil dan Product](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=3JUtW0&nav=MTVfe0U3QTJGQUFCLTU3RDQtNEE2MS1CREM5LTZCOThDRTE0QTZDRH0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/crude_oil_and_products/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| produk | `produk` | Categorical | - | Crude Oil, Oil Fuel (BBM), atau LPG |
| komponen | `komponen` | Categorical | - | Production, Export, Import, atau Domestic. Export digambar negatif di bawah sumbu |
| nilai | `nilai` | Numeric (Decimal) | Tergantung kolom | Nilai per komponen |
| satuan | `satuan` | Categorical | - | Million Barrel (crude), Thousand Barrel (oil fuel, Gambar 4), Thousand MTon (LPG, Gambar 5) |
| pertumbuhan_yoy_persen | `pertumbuhan_yoy_persen` | Numeric (Decimal) | % | Pertumbuhan dibanding tahun sebelumnya, dari teks. Kosong bila tidak disebut |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class CrudeOilAndProductsRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    produk: str | None = Field(default=None, alias="produk", description="Crude Oil, Oil Fuel (BBM), atau LPG")
    komponen: str | None = Field(default=None, alias="komponen", description="Production, Export, Import, atau Domestic. Export digambar negatif di bawah sumbu")
    nilai: str | None = Field(default=None, alias="nilai", description="Nilai per komponen")
    satuan: str | None = Field(default=None, alias="satuan", description="Million Barrel (crude), Thousand Barrel (oil fuel, Gambar 4), Thousand MTon (LPG, Gambar 5)")
    pertumbuhan_yoy_persen: str | None = Field(default=None, alias="pertumbuhan_yoy_persen", description="Pertumbuhan dibanding tahun sebelumnya, dari teks. Kosong bila tidak disebut")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
