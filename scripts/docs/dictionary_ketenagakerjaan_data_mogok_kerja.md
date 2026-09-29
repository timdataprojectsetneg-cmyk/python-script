# Data Dictionary: Data Mogok Kerja

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Data Mogok Kerja`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=Du6rbu&nav=MTVfezRDMkY1NzIzLTdBQUEtNEIzQS1CQ0YwLTRBOTA4QkUxRTgzMn0)
- Target module: `ingestion/usecases/ketenagakerjaan/data_mogok_kerja/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Wilayah | `wilayah` | String | - | Provinsi (perlu verifikasi struktur kolom sebenarnya). |
| Kasus | `kasus` | Integer | Kejadian | Jumlah kejadian mogok kerja tercatat. |
| Tenaga Kerja yang Terlibat | `tenaga_kerja_yang_terlibat` | Integer | Orang | Jumlah peserta mogok kerja tercatat. |
| Tahun | `tahun` | Integer | - | Tahun penarikan data |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class DataMogokKerjaRecord(BaseModel):
    wilayah: str | None = Field(default=None, alias="Wilayah")
    kasus: int | None = Field(default=None, alias="Kasus")
    tenaga_kerja_yang_terlibat: int | None = Field(default=None, alias="Tenaga Kerja yang Terlibat")
    tahun: int | None = Field(default=None, alias="Tahun")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
