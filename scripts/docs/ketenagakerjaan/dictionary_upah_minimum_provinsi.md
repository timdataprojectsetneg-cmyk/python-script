# Data Dictionary: Upah Minimum Provinsi (UMP)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Upah Minimum Provinsi (UMP)`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=y38ycW&nav=MTVfe0E2ODc2NTVDLTExQzAtNDQ4Qi1BRkQ4LTNDMzk1N0M4Qzk5Q30)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/upah_minimum_provinsi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Nama provinsi. |
| Nilai_UMP | `nilai_ump` | Decimal | Rupiah | Besaran UMP dalam Rupiah. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class UpahMinimumProvinsiRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi.")
    nilai_ump: float | None = Field(default=None, alias="Nilai_UMP", description="Besaran UMP dalam Rupiah.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
