# Data Dictionary: Data Mogok Kerja

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Data Mogok Kerja`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Data Mogok Kerja](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=4dPDFu&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wQTAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/data_mogok_kerja/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Provinsi lokasi mogok kerja ("Jumlah" = nasional). |
| Periode | `periode` | String | - | Periode data, kumulatif sejak Januari. |
| Jumlah_Kasus | `jumlah_kasus` | Integer | Kasus | Jumlah kasus mogok kerja; "-" = tidak ada kasus. |
| TK_Terlibat | `tk_terlibat` | Integer | Orang | Jumlah tenaga kerja yang terlibat mogok. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class DataMogokKerjaRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Provinsi lokasi mogok kerja (\"Jumlah\" = nasional).")
    periode: str | None = Field(default=None, alias="Periode", description="Periode data, kumulatif sejak Januari.")
    jumlah_kasus: int | None = Field(default=None, alias="Jumlah_Kasus", description="Jumlah kasus mogok kerja; \"-\" = tidak ada kasus.")
    tk_terlibat: int | None = Field(default=None, alias="TK_Terlibat", description="Jumlah tenaga kerja yang terlibat mogok.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
