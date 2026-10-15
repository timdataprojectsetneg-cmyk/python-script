# Data Dictionary: Signal Ketenagakerjaan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Signal Ketenagakerjaan`
- Publisher: The Signal
- Data access: `scraper`
- Update frequency: Daily
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=IHPj3g&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0xQjAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/the_signal/signal_ketenagakerjaan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tanggal | `tanggal` | Date | - | Tanggal publikasi berita. |
| Judul_Berita | `judul_berita` | String | - | Judul berita. |
| Isi_Berita | `isi_berita` | Text | - | Isi berita (pada halaman rubrik tampil sebagai ringkasan). |
| Sumber_Berita | `sumber_berita` | String | - | Nama media (The Signal). |
| Url_Berita | `url_berita` | String | URL | Tautan artikel. |
| Foto_Ilustrasi | `foto_ilustrasi` | String | URL | Tautan foto ilustrasi artikel. |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class SignalKetenagakerjaanRecord(BaseModel):
    tanggal: date | None = Field(default=None, alias="Tanggal", description="Tanggal publikasi berita.")
    judul_berita: str | None = Field(default=None, alias="Judul_Berita", description="Judul berita.")
    isi_berita: str | None = Field(default=None, alias="Isi_Berita", description="Isi berita (pada halaman rubrik tampil sebagai ringkasan).")
    sumber_berita: str | None = Field(default=None, alias="Sumber_Berita", description="Nama media (The Signal).")
    url_berita: str | None = Field(default=None, alias="Url_Berita", description="Tautan artikel.")
    foto_ilustrasi: str | None = Field(default=None, alias="Foto_Ilustrasi", description="Tautan foto ilustrasi artikel.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
