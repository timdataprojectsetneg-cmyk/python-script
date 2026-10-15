# Data Dictionary: BPS Inflasi YoY

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `BPS Inflasi YoY`
- Publisher: BPS
- Data access: `scraper`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - BPS Inflasi YoY](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=uq9XTs&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wRTAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/bps/bps_inflasi_yoy/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | String | - | Bulan dan tahun. |
| Inflasi_YoY | `inflasi_yoy` | Decimal | Persen | Inflasi year-on-year nasional. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsInflasiYoyRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Bulan dan tahun.")
    inflasi_yoy: float | None = Field(default=None, alias="Inflasi_YoY", description="Inflasi year-on-year nasional.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
