# Data Dictionary: Perjanjian Perdagangan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Perjanjian Perdagangan`
- Publisher: Kemendag
- Data access: `scraper`
- Update frequency: Sesuai perubahan perjanjian
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Hubungan Bilateral (1).xlsx
- Target module: `ingestion/usecases/geopolitik/kemendag/perjanjian_perdagangan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Nama Perjanjian | `nama_perjanjian` | String | - | Nama perjanjian pada daftar resmi Kemendag. |
| Status menurut Sumber | `status_menurut_sumber` | String | - | Status pada periode referensi daftar. |
| Tautan Detail | `tautan_detail` | String | URL | Tautan detail perjanjian yang disediakan halaman sumber. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PerjanjianPerdaganganRecord(BaseModel):
    nama_perjanjian: str | None = Field(default=None, alias="Nama Perjanjian", description="Nama perjanjian pada daftar resmi Kemendag.")
    status_menurut_sumber: str | None = Field(default=None, alias="Status menurut Sumber", description="Status pada periode referensi daftar.")
    tautan_detail: str | None = Field(default=None, alias="Tautan Detail", description="Tautan detail perjanjian yang disediakan halaman sumber.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
