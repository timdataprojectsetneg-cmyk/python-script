# Data Dictionary: Upah Minimum Provinsi (UMP)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Upah Minimum Provinsi (UMP)`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - UMP](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=agCbn6&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wQTAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/upah_minimum_provinsi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Nama provinsi. |
| Upah_Minimum | `upah_minimum` | Decimal | Rupiah | Besaran UMP tahun 2026. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class UpahMinimumProvinsiRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi.")
    upah_minimum: float | None = Field(default=None, alias="Upah_Minimum", description="Besaran UMP tahun 2026.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
