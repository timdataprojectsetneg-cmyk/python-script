# Data Dictionary: Coal

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Coal`
- Publisher: esdm
- Data access: `pdf`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_ES Coal](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=2MVWXN&nav=MTVfe0YzOTk2MkJCLTZDODItNDNBRC1BQUIwLTMzQTFENkQzQzI5OH0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/coal/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun neraca batubara (grafik 2019–2025) |
| komponen | `komponen` | Categorical | - | Production, Export, Import, atau Domestic (penjualan domestik) |
| volume | `volume` | Numeric (Decimal) | Million Ton | Volume per komponen. Export digambar di bawah sumbu nol dan ditulis dalam kurung, jadi bertanda negatif di grafik |
| pertumbuhan_yoy_persen | `pertumbuhan_yoy_persen` | Numeric (Decimal) | % | Pertumbuhan dibanding tahun sebelumnya, dari teks. Kosong bila tidak disebut |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class CoalRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun neraca batubara (grafik 2019–2025)")
    komponen: str | None = Field(default=None, alias="komponen", description="Production, Export, Import, atau Domestic (penjualan domestik)")
    volume: str | None = Field(default=None, alias="volume", description="Volume per komponen. Export digambar di bawah sumbu nol dan ditulis dalam kurung, jadi bertanda negatif di grafik")
    pertumbuhan_yoy_persen: str | None = Field(default=None, alias="pertumbuhan_yoy_persen", description="Pertumbuhan dibanding tahun sebelumnya, dari teks. Kosong bila tidak disebut")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
