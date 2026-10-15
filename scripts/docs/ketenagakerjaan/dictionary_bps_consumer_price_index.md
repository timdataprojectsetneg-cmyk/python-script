# Data Dictionary: BPS Consumer Price Index

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `BPS Consumer Price Index`
- Publisher: BPS
- Data access: `api`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - BPS Consumer Price Index](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=XX17C6&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0xMDAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/bps/bps_consumer_price_index/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Nama provinsi (INDONESIA = nasional). |
| Januari | `januari` | Decimal | Indeks | IHK (2022=100) bulan Januari 2026; "-" = belum rilis. |
| Februari | `februari` | Decimal | Indeks | IHK (2022=100) bulan Februari 2026; "-" = belum rilis. |
| Maret | `maret` | Decimal | Indeks | IHK (2022=100) bulan Maret 2026; "-" = belum rilis. |
| April | `april` | Decimal | Indeks | IHK (2022=100) bulan April 2026; "-" = belum rilis. |
| Mei | `mei` | Decimal | Indeks | IHK (2022=100) bulan Mei 2026; "-" = belum rilis. |
| Juni | `juni` | Decimal | Indeks | IHK (2022=100) bulan Juni 2026; "-" = belum rilis. |
| Juli | `juli` | Decimal | Indeks | IHK (2022=100) bulan Juli 2026; "-" = belum rilis. |
| Agustus | `agustus` | Decimal | Indeks | IHK (2022=100) bulan Agustus 2026; "-" = belum rilis. |
| September | `september` | Decimal | Indeks | IHK (2022=100) bulan September 2026; "-" = belum rilis. |
| Oktober | `oktober` | Decimal | Indeks | IHK (2022=100) bulan Oktober 2026; "-" = belum rilis. |
| November | `november` | Decimal | Indeks | IHK (2022=100) bulan November 2026; "-" = belum rilis. |
| Desember | `desember` | Decimal | Indeks | IHK (2022=100) bulan Desember 2026; "-" = belum rilis. |
| Tahunan | `tahunan` | Decimal | Indeks | IHK tahunan (terisi setelah Desember). |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsConsumerPriceIndexRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (INDONESIA = nasional).")
    januari: float | None = Field(default=None, alias="Januari", description="IHK (2022=100) bulan Januari 2026; \"-\" = belum rilis.")
    februari: float | None = Field(default=None, alias="Februari", description="IHK (2022=100) bulan Februari 2026; \"-\" = belum rilis.")
    maret: float | None = Field(default=None, alias="Maret", description="IHK (2022=100) bulan Maret 2026; \"-\" = belum rilis.")
    april: float | None = Field(default=None, alias="April", description="IHK (2022=100) bulan April 2026; \"-\" = belum rilis.")
    mei: float | None = Field(default=None, alias="Mei", description="IHK (2022=100) bulan Mei 2026; \"-\" = belum rilis.")
    juni: float | None = Field(default=None, alias="Juni", description="IHK (2022=100) bulan Juni 2026; \"-\" = belum rilis.")
    juli: float | None = Field(default=None, alias="Juli", description="IHK (2022=100) bulan Juli 2026; \"-\" = belum rilis.")
    agustus: float | None = Field(default=None, alias="Agustus", description="IHK (2022=100) bulan Agustus 2026; \"-\" = belum rilis.")
    september: float | None = Field(default=None, alias="September", description="IHK (2022=100) bulan September 2026; \"-\" = belum rilis.")
    oktober: float | None = Field(default=None, alias="Oktober", description="IHK (2022=100) bulan Oktober 2026; \"-\" = belum rilis.")
    november: float | None = Field(default=None, alias="November", description="IHK (2022=100) bulan November 2026; \"-\" = belum rilis.")
    desember: float | None = Field(default=None, alias="Desember", description="IHK (2022=100) bulan Desember 2026; \"-\" = belum rilis.")
    tahunan: float | None = Field(default=None, alias="Tahunan", description="IHK tahunan (terisi setelah Desember).")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
