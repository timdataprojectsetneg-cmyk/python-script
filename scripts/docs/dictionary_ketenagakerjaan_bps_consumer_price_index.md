# Data Dictionary: BPS Consumer Price Index

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `BPS Consumer Price Index`
- Publisher: BPS
- Data access: `api`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=D3AjF1&nav=MTVfezNCN0I5QjEzLTVCQUEtNDhFRC1BNjA5LUZFNjA5QUE1M0E2NH0)
- Target module: `ingestion/usecases/ketenagakerjaan/bps/bps_consumer_price_index/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Nama provinsi (38 provinsi). |
| Januari | `januari` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Februari | `februari` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Maret | `maret` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| April | `april` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Mei | `mei` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Juni | `juni` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Juli | `juli` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Agustus | `agustus` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| September | `september` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Oktober | `oktober` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| November | `november` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Desember | `desember` | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Tahun | `tahun` | String | - | tahun rilis. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsConsumerPriceIndexRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (38 provinsi).")
    januari: float | None = Field(default=None, alias="Januari", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    februari: float | None = Field(default=None, alias="Februari", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    maret: float | None = Field(default=None, alias="Maret", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    april: float | None = Field(default=None, alias="April", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    mei: float | None = Field(default=None, alias="Mei", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    juni: float | None = Field(default=None, alias="Juni", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    juli: float | None = Field(default=None, alias="Juli", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    agustus: float | None = Field(default=None, alias="Agustus", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    september: float | None = Field(default=None, alias="September", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    oktober: float | None = Field(default=None, alias="Oktober", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    november: float | None = Field(default=None, alias="November", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    desember: float | None = Field(default=None, alias="Desember", description="Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan")
    tahun: str | None = Field(default=None, alias="Tahun", description="tahun rilis.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
