# Data Dictionary: Sengketa Dagang Indonesia

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Sengketa Dagang Indonesia`
- Publisher: WTO
- Data access: `scraper`
- Update frequency: Sesuai proses sengketa
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Hubungan Bilateral (1).xlsx
- Target module: `ingestion/usecases/geopolitik/wto/sengketa_dagang/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Nomor Sengketa | `nomor_sengketa` | String | ID | Nomor kasus WTO. |
| Isu | `isu` | String | - | Pokok isu sengketa, diringkas. |
| Tanggal Tahapan | `tanggal_tahapan` | Date | Tanggal | Tanggal kejadian prosedural pada kronologi WTO. |
| Tahapan | `tahapan` | String | - | Ringkasan tindakan pihak/DSB/panel. |
| URL Kasus | `url_kasus` | String | URL | Halaman resmi kronologi dan dokumen kasus. |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class SengketaDagangIndonesiaRecord(BaseModel):
    nomor_sengketa: str | None = Field(default=None, alias="Nomor Sengketa", description="Nomor kasus WTO.")
    isu: str | None = Field(default=None, alias="Isu", description="Pokok isu sengketa, diringkas.")
    tanggal_tahapan: date | None = Field(default=None, alias="Tanggal Tahapan", description="Tanggal kejadian prosedural pada kronologi WTO.")
    tahapan: str | None = Field(default=None, alias="Tahapan", description="Ringkasan tindakan pihak/DSB/panel.")
    url_kasus: str | None = Field(default=None, alias="URL Kasus", description="Halaman resmi kronologi dan dokumen kasus.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
