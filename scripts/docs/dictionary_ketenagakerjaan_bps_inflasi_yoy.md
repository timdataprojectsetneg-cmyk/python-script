# Data Dictionary: BPS Inflasi YoY

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `BPS Inflasi YoY`
- Publisher: BPS
- Data access: `scraper`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=ap5U9F&nav=MTVfezAyRjVGRDIyLTc0OUQtNEYyQy04N0E0LTE2QzYwQTI3MkRCNX0)
- Target module: `ingestion/usecases/ketenagakerjaan/bps/bps_inflasi_yoy/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | String | - | Bulan dan tahun rilis (misal: Agustus 2026). |
| Inflasi_YoY | `inflasi_yoy` | Decimal | % | Inflasi year-on-year dibanding bulan yang sama tahun sebelumnya. |
| Inflasi_MtM | `inflasi_mtm` | Decimal | % | Inflasi month-to-month dibanding bulan sebelumnya. |
| Komponen_Pendorong | `komponen_pendorong` | String | - | Kelompok pengeluaran/komoditas utama pendorong inflasi bulan tersebut (dari narasi siaran pers). |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsInflasiYoyRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode")
    inflasi_yoy: float | None = Field(default=None, alias="Inflasi_YoY")
    inflasi_mtm: float | None = Field(default=None, alias="Inflasi_MtM")
    komponen_pendorong: str | None = Field(default=None, alias="Komponen_Pendorong")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
