# Data Dictionary: BPS Inflasi YoY

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `Ketenagakerjaan`
- Source: `BPS Inflasi YoY`
- Publisher: BPS
- Data access: `scraper`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=ap5U9F&nav=MTVfezAyRjVGRDIyLTc0OUQtNEYyQy04N0E0LTE2QzYwQTI3MkRCNX0)
- Target module: `ingestion/usecases/ketenagakerjaan/bps_inflasi_yoy/models.py`

## Fields

| Label | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|
| Periode | String | - | Bulan dan tahun rilis (misal: Agustus 2026). |
| Inflasi_YoY | Decimal | % | Inflasi year-on-year dibanding bulan yang sama tahun sebelumnya. |
| Inflasi_MtM | Decimal | % | Inflasi month-to-month dibanding bulan sebelumnya. |
| Komponen_Pendorong | String | - | Kelompok pengeluaran/komoditas utama pendorong inflasi bulan tersebut (dari narasi siaran pers). |
| Sample Data | - | - | - |
| CATATAN: siaran pers BPS dirilis tiap awal bulan dan DIJAMIN current, tetapi URL-nya berganti tiap bulan (mengandung tanggal rilis dan nomor seri). Contoh terverifikasi: rilis 1 September 2026 menyebutkan inflasi YoY Agustus 2026 sebesar 3,19%. Sifatnya NASIONAL (bukan per provinsi/kota) - untuk breakdown wilayah lihat sheet 'IHK 38 Provinsi (Tabel Dinamis)'. | - | - | - |
| Periode | Inflasi_YoY | Inflasi_MtM | - |
| Agustus 2026 | 0.0319 | 0.0021 | - |
| Sample Data: | - | - | - |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsInflasiYoyRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode")
    inflasi_yoy: float | None = Field(default=None, alias="Inflasi_YoY")
    inflasi_mtm: float | None = Field(default=None, alias="Inflasi_MtM")
    komponen_pendorong: str | None = Field(default=None, alias="Komponen_Pendorong")
    sample_data: str | None = Field(default=None, alias="Sample Data")
    catatan_siaran_pers_bps_dirilis_tiap_awal_bulan: str | None = Field(default=None, alias="CATATAN: siaran pers BPS dirilis tiap awal bulan dan DIJAMIN current, tetapi URL-nya berganti tiap bulan (mengandung tanggal rilis dan nomor seri). Contoh terverifikasi: rilis 1 September 2026 menyebutkan inflasi YoY Agustus 2026 sebesar 3,19%. Sifatnya NASIONAL (bukan per provinsi/kota) - untuk breakdown wilayah lihat sheet 'IHK 38 Provinsi (Tabel Dinamis)'.")
    periode: str | None = Field(default=None, alias="Periode")
    agustus_2026: str | None = Field(default=None, alias="Agustus 2026")
    sample_data: str | None = Field(default=None, alias="Sample Data:")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
