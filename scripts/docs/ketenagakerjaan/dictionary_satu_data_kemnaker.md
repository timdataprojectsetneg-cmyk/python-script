# Data Dictionary: Satu Data Kemnaker

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Satu Data Kemnaker`
- Publisher: Kemnaker
- Data access: `api`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=K5AnJD&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0xRTAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/satu_data_kemnaker/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| judul | `judul` | String | - | - |
| link_file | `link_file` | Integer | link | - |
| abstraksi | `abstraksi` | Integer | - | - |
| created_at | `created_at` | String | YYYY-MM-DDTHH:MM:SS | Tanggal Pembuatan |
| updated_at | `updated_at` | String | YYYY-MM-DDTHH:MM:SS | - |
| is_deleted | `is_deleted` | bool | - | - |
| deleted_at | `deleted_at` | string | YYYY-MM-DDTHH:MM:SS | - |
| minio_file | `minio_file` | String | - | - |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class SatuDataKemnakerRecord(BaseModel):
    judul: str | None = Field(default=None, alias="judul")
    link_file: int | None = Field(default=None, alias="link_file")
    abstraksi: int | None = Field(default=None, alias="abstraksi")
    created_at: str | None = Field(default=None, alias="created_at", description="Tanggal Pembuatan")
    updated_at: str | None = Field(default=None, alias="updated_at")
    is_deleted: bool | None = Field(default=None, alias="is_deleted")
    deleted_at: str | None = Field(default=None, alias="deleted_at")
    minio_file: str | None = Field(default=None, alias="minio_file")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
