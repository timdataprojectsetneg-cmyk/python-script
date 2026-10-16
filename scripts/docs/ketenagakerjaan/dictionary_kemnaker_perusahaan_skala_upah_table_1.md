# Data Dictionary: Kemnaker Perusahaan Skala Upah Table 1

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Kemnaker Perusahaan Skala Upah Table 1`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Kemnaker Perusahaan Skala Upah Table 1](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=QC8wae&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0xNzAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/kemnaker_perusahaan_skala_upah_table_1/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Nama provinsi ("Jumlah" = nasional). |
| Mikro | `mikro` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah skala Mikro (1–4 TK). |
| Kecil | `kecil` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah skala Kecil (5–19 TK). |
| Menengah | `menengah` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah skala Menengah (20–99 TK). |
| Besar | `besar` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah skala Besar (≥100 TK). |
| Tidak_Teridentifikasi | `tidak_teridentifikasi` | Integer | Perusahaan | Perusahaan yang melaporkan Struktur Skala Upah yang belum melaporkan informasi tenaga kerja. |
| Jumlah | `jumlah` | Integer | Perusahaan | Total seluruh skala. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KemnakerPerusahaanSkalaUpahTable1Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (\"Jumlah\" = nasional).")
    mikro: int | None = Field(default=None, alias="Mikro", description="Perusahaan yang melaporkan Struktur Skala Upah skala Mikro (1–4 TK).")
    kecil: int | None = Field(default=None, alias="Kecil", description="Perusahaan yang melaporkan Struktur Skala Upah skala Kecil (5–19 TK).")
    menengah: int | None = Field(default=None, alias="Menengah", description="Perusahaan yang melaporkan Struktur Skala Upah skala Menengah (20–99 TK).")
    besar: int | None = Field(default=None, alias="Besar", description="Perusahaan yang melaporkan Struktur Skala Upah skala Besar (≥100 TK).")
    tidak_teridentifikasi: int | None = Field(default=None, alias="Tidak_Teridentifikasi", description="Perusahaan yang melaporkan Struktur Skala Upah yang belum melaporkan informasi tenaga kerja.")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total seluruh skala.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
