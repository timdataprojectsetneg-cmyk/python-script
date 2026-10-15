# Data Dictionary: UMK Kalimantan Tengah

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `UMK Kalimantan Tengah`
- Publisher: GoodStats
- Data access: `scraper`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - UMK](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=joPYuh&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wQjAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/goodstats/umk_kalimantan_tengah/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Kabupaten Kota | `kabupaten_kota` | String | - | Nama Kabupaten Kota |
| umk | `umk` | Integer | Rupiah | Jumlah UMK |
| tahun | `tahun` | Integer | Tahun | Tahun Perhitungan |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class UmkKalimantanTengahRecord(BaseModel):
    kabupaten_kota: str | None = Field(default=None, alias="Kabupaten Kota", description="Nama Kabupaten Kota")
    umk: int | None = Field(default=None, alias="umk", description="Jumlah UMK")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun Perhitungan")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
