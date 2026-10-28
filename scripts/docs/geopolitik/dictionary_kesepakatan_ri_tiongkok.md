# Data Dictionary: Kesepakatan RI Tiongkok

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Kesepakatan RI Tiongkok`
- Publisher: Setpres
- Data access: `scraper`
- Update frequency: Sesuai penandatanganan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Hubungan Bilateral (1).xlsx
- Target module: `ingestion/usecases/geopolitik/setpres/kesepakatan_ri_tiongkok/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tanggal | `tanggal` | Date | Tanggal | Tanggal penandatanganan yang diumumkan. |
| Topik Kesepakatan | `topik_kesepakatan` | String | - | Ringkasan topik dokumen, bukan judul legal yang direka. |
| Pihak Indonesia | `pihak_indonesia` | String | - | Institusi Indonesia yang disebut sumber. |
| Pihak Mitra | `pihak_mitra` | String | - | Institusi Tiongkok yang disebut sumber. |
| Status Bukti | `status_bukti` | String | - | Status penandatanganan berdasarkan siaran pers, bukan status implementasi. |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class KesepakatanRiTiongkokRecord(BaseModel):
    tanggal: date | None = Field(default=None, alias="Tanggal", description="Tanggal penandatanganan yang diumumkan.")
    topik_kesepakatan: str | None = Field(default=None, alias="Topik Kesepakatan", description="Ringkasan topik dokumen, bukan judul legal yang direka.")
    pihak_indonesia: str | None = Field(default=None, alias="Pihak Indonesia", description="Institusi Indonesia yang disebut sumber.")
    pihak_mitra: str | None = Field(default=None, alias="Pihak Mitra", description="Institusi Tiongkok yang disebut sumber.")
    status_bukti: str | None = Field(default=None, alias="Status Bukti", description="Status penandatanganan berdasarkan siaran pers, bukan status implementasi.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
