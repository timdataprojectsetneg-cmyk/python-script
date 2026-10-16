# Data Dictionary: Kemnaker Perusahaan WLKP

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Kemnaker Perusahaan WLKP`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Kemnaker Perusahaan WLKP](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=j79xl1&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0xNDAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/kemnaker_perusahaan_wlkp/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Nama provinsi ("Jumlah" = nasional). |
| Mikro | `mikro` | Integer | Perusahaan | Perusahaan terlapor WLKP skala Mikro (1–4 TK). |
| Kecil | `kecil` | Integer | Perusahaan | Perusahaan terlapor WLKP skala Kecil (5–19 TK). |
| Menengah | `menengah` | Integer | Perusahaan | Perusahaan terlapor WLKP skala Menengah (20–99 TK). |
| Besar | `besar` | Integer | Perusahaan | Perusahaan terlapor WLKP skala Besar (≥100 TK). |
| Belum_Teridentifikasi | `belum_teridentifikasi` | Integer | Perusahaan | Perusahaan terlapor WLKP yang belum melaporkan informasi tenaga kerja. |
| Jumlah | `jumlah` | Integer | Perusahaan | Total seluruh skala. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KemnakerPerusahaanWlkpRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (\"Jumlah\" = nasional).")
    mikro: int | None = Field(default=None, alias="Mikro", description="Perusahaan terlapor WLKP skala Mikro (1–4 TK).")
    kecil: int | None = Field(default=None, alias="Kecil", description="Perusahaan terlapor WLKP skala Kecil (5–19 TK).")
    menengah: int | None = Field(default=None, alias="Menengah", description="Perusahaan terlapor WLKP skala Menengah (20–99 TK).")
    besar: int | None = Field(default=None, alias="Besar", description="Perusahaan terlapor WLKP skala Besar (≥100 TK).")
    belum_teridentifikasi: int | None = Field(default=None, alias="Belum_Teridentifikasi", description="Perusahaan terlapor WLKP yang belum melaporkan informasi tenaga kerja.")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total seluruh skala.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
