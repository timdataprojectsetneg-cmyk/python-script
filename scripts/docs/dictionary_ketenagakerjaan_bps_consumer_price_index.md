# Data Dictionary: BPS Consumer Price Index

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `BPS Consumer Price Index`
- Publisher: BPS
- Data access: `api`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=D3AjF1&nav=MTVfezNCN0I5QjEzLTVCQUEtNDhFRC1BNjA5LUZFNjA5QUE1M0E2NH0)
- Target module: `ingestion/usecases/ketenagakerjaan/bps/bps_consumer_price_index/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Nama provinsi (38 provinsi). |
| (January, Ferbruary, .., December) | `january_ferbruary_december` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Tahun | `tahun` | String | - | tahun rilis. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsConsumerPriceIndexRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi")
    january_ferbruary_december: float | None = Field(default=None, alias="(January, Ferbruary, .., December)")
    tahun: str | None = Field(default=None, alias="Tahun")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
