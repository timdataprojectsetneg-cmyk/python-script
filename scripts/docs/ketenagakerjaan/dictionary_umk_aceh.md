# Data Dictionary: UMK Aceh

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `UMK Aceh`
- Publisher: GoodStats
- Data access: `scraper`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=SXiQL6&nav=MTVfezc5Q0FERjY4LTNGQTEtNDMxMS1CMzUxLTYyQzI3RUE2Qzg4Qn0)
- Target module: `ingestion/usecases/ketenagakerjaan/goodstats/umk_aceh/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Kabupaten Kota | `kabupaten_kota` | String | - | Nama Kabupaten Kota |
| umk | `umk` | Integer | Rupiah | Jumlah UMK |
| tahun | `tahun` | Integer | Tahun | Tahun Perhitungan |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class UmkAcehRecord(BaseModel):
    kabupaten_kota: str | None = Field(default=None, alias="Kabupaten Kota", description="Nama Kabupaten Kota")
    umk: int | None = Field(default=None, alias="umk", description="Jumlah UMK")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun Perhitungan")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
