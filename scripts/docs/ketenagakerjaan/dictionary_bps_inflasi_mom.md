# Data Dictionary: BPS Inflasi MoM

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `BPS Inflasi MoM`
- Publisher: BPS
- Data access: `api`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - BPS Inflasi MoM](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=inVlDn&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wRjAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/bps/bps_inflasi_mom/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Kota_Inflasi | `kota_inflasi` | String | - | Kab/kota titik pantau IHK BPS (INDONESIA = nasional). |
| Januari | `januari` | Decimal | Persen | Inflasi m-to-m bulan Januari 2026; "-" = belum rilis. |
| Februari | `februari` | Decimal | Persen | Inflasi m-to-m bulan Februari 2026; "-" = belum rilis. |
| Maret | `maret` | Decimal | Persen | Inflasi m-to-m bulan Maret 2026; "-" = belum rilis. |
| April | `april` | Decimal | Persen | Inflasi m-to-m bulan April 2026; "-" = belum rilis. |
| Mei | `mei` | Decimal | Persen | Inflasi m-to-m bulan Mei 2026; "-" = belum rilis. |
| Juni | `juni` | Decimal | Persen | Inflasi m-to-m bulan Juni 2026; "-" = belum rilis. |
| Juli | `juli` | Decimal | Persen | Inflasi m-to-m bulan Juli 2026; "-" = belum rilis. |
| Agustus | `agustus` | Decimal | Persen | Inflasi m-to-m bulan Agustus 2026; "-" = belum rilis. |
| September | `september` | Decimal | Persen | Inflasi m-to-m bulan September 2026; "-" = belum rilis. |
| Oktober | `oktober` | Decimal | Persen | Inflasi m-to-m bulan Oktober 2026; "-" = belum rilis. |
| November | `november` | Decimal | Persen | Inflasi m-to-m bulan November 2026; "-" = belum rilis. |
| Desember | `desember` | Decimal | Persen | Inflasi m-to-m bulan Desember 2026; "-" = belum rilis. |
| Tahunan | `tahunan` | Decimal | Persen | Inflasi tahun kalender (terisi setelah Desember). |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsInflasiMomRecord(BaseModel):
    kota_inflasi: str | None = Field(default=None, alias="Kota_Inflasi", description="Kab/kota titik pantau IHK BPS (INDONESIA = nasional).")
    januari: float | None = Field(default=None, alias="Januari", description="Inflasi m-to-m bulan Januari 2026; \"-\" = belum rilis.")
    februari: float | None = Field(default=None, alias="Februari", description="Inflasi m-to-m bulan Februari 2026; \"-\" = belum rilis.")
    maret: float | None = Field(default=None, alias="Maret", description="Inflasi m-to-m bulan Maret 2026; \"-\" = belum rilis.")
    april: float | None = Field(default=None, alias="April", description="Inflasi m-to-m bulan April 2026; \"-\" = belum rilis.")
    mei: float | None = Field(default=None, alias="Mei", description="Inflasi m-to-m bulan Mei 2026; \"-\" = belum rilis.")
    juni: float | None = Field(default=None, alias="Juni", description="Inflasi m-to-m bulan Juni 2026; \"-\" = belum rilis.")
    juli: float | None = Field(default=None, alias="Juli", description="Inflasi m-to-m bulan Juli 2026; \"-\" = belum rilis.")
    agustus: float | None = Field(default=None, alias="Agustus", description="Inflasi m-to-m bulan Agustus 2026; \"-\" = belum rilis.")
    september: float | None = Field(default=None, alias="September", description="Inflasi m-to-m bulan September 2026; \"-\" = belum rilis.")
    oktober: float | None = Field(default=None, alias="Oktober", description="Inflasi m-to-m bulan Oktober 2026; \"-\" = belum rilis.")
    november: float | None = Field(default=None, alias="November", description="Inflasi m-to-m bulan November 2026; \"-\" = belum rilis.")
    desember: float | None = Field(default=None, alias="Desember", description="Inflasi m-to-m bulan Desember 2026; \"-\" = belum rilis.")
    tahunan: float | None = Field(default=None, alias="Tahunan", description="Inflasi tahun kalender (terisi setelah Desember).")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
