# Data Dictionary: Signal Ketenagakerjaan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Signal Ketenagakerjaan`
- Publisher: The Signal
- Data access: `scraper`
- Update frequency: Daily
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=6aybEs&nav=MTVfe0IwMzZEMkY1LTlDRUUtNDkzMy05ODM0LUNCRThENkVEQkQzNH0)
- Target module: `ingestion/usecases/ketenagakerjaan/the_signal/signal_ketenagakerjaan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tanggal | `tanggal` | String | - | Tanggal publikasi berita. |
| Judul_Berita | `judul_berita` | String | - | Judul berita. |
| Isi_Berita | `isi_berita` | String | - | Isi lengkap pemberitaan. |
| Sumber_Berita | `sumber_berita` | String | - | Nama sumber pemberitaan (teks, bukan URL). |
| Url_Berita | `url_berita` | String | - | URL artikel. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class SignalKetenagakerjaanRecord(BaseModel):
    tanggal: str | None = Field(default=None, alias="Tanggal")
    judul_berita: str | None = Field(default=None, alias="Judul_Berita")
    isi_berita: str | None = Field(default=None, alias="Isi_Berita")
    sumber_berita: str | None = Field(default=None, alias="Sumber_Berita")
    url_berita: str | None = Field(default=None, alias="Url_Berita")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
