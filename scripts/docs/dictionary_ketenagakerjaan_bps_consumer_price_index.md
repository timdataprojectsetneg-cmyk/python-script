# Data Dictionary: BPS Consumer Price Index

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `Ketenagakerjaan`
- Source: `BPS Consumer Price Index`
- Publisher: BPS
- Data access: `api`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=D3AjF1&nav=MTVfezNCN0I5QjEzLTVCQUEtNDhFRC1BNjA5LUZFNjA5QUE1M0E2NH0)
- Target module: `ingestion/usecases/ketenagakerjaan/bps_consumer_price_index/models.py`

## Fields

| Label | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|
| Provinsi | String | - | Nama provinsi (38 provinsi). |
| (January, Ferbruary, .., December) | Decimal | Indeks (2022=100) | Nilai Indeks Harga Konsumen dengan tahun dasar 2022. Per-Bulan |
| Tahun | String | - | tahun rilis. |
| 38 Province (2022=100) | - | - | - |
| PROV ACEH | 114.23 | 113.96 | 114.01 |
| PROV SUMATERA UTARA | 111.41 | 111.66 | 111.51 |
| PROV SUMATERA BARAT | 111.12 | 111.45 | 111.49 |
| PROV RIAU | 111.7 | 112.06 | 111.84 |
| PROV JAMBI | 109.98 | 110.62 | 110.77 |
| PROV SUMATERA SELATAN | 110.18 | 110.82 | 111.14 |
| PROV BENGKULU | 108.08 | 108.79 | 109.09 |
| PROV LAMPUNG | 109.71 | 110.11 | 110.32 |
| PROV KEPULAUAN BANGKA BELITUNG | 107.44 | 106.75 | 107.19 |
| PROV KEPULAUAN RIAU | 110.98 | 111.47 | 111.56 |
| PROV DKI JAKARTA | 108.22 | 108.9 | 109.45 |
| PROV JAWA BARAT | 110.05 | 110.94 | 111.52 |
| PROV JAWA TENGAH | 109.6 | 110.43 | 111.06 |
| PROV DI YOGYAKARTA | 109.75 | 110.5 | 111 |
| PROV JAWA TIMUR | 110.03 | 111.07 | 111.5 |
| PROV BANTEN | 109.16 | 110.18 | 110.7 |
| PROV BALI | 110.63 | 111.4 | 112.02 |
| PROV NUSA TENGGARA BARAT | 110.56 | 111.49 | 112.39 |
| PROV NUSA TENGGARA TIMUR | 109.65 | 110.14 | 110.41 |
| PROV KALIMANTAN BARAT | 109.09 | 109.65 | 109.92 |
| PROV KALIMANTAN TENGAH | 110.4 | 110.91 | 111.51 |
| PROV KALIMANTAN SELATAN | 111.28 | 112.24 | 112.8 |
| PROV KALIMANTAN TIMUR | 109.84 | 110.5 | 111.3 |
| PROV KALIMANTAN UTARA | 108.55 | 109.06 | 109.68 |
| PROV SULAWESI UTARA | 109.33 | 110.44 | 110.72 |
| PROV SULAWESI TENGAH | 110.72 | 111.61 | 112.03 |
| PROV SULAWESI SELATAN | 109.79 | 110.93 | 111.59 |
| PROV SULAWESI TENGGARA | 110.37 | 111.09 | 111.55 |
| PROV GORONTALO | 109.6 | 110.51 | 110.78 |
| PROV SULAWESI BARAT | 110.21 | 110.53 | 110.62 |
| PROV MALUKU | 111.65 | 112.3 | 111.46 |
| PROV MALUKU UTARA | 111.71 | 112.64 | 112.03 |
| PROV PAPUA BARAT | 110.76 | 110.04 | 110.1 |
| PROV PAPUA BARAT DAYA | 107.82 | 107.21 | 108.33 |
| PROV PAPUA | 107.95 | 108.02 | 108.78 |
| PROV PAPUA SELATAN | 112.26 | 112.92 | 113.32 |
| PROV PAPUA TENGAH | 113.94 | 113.91 | 114.21 |
| PROV PAPUA PEGUNUNGAN | 115.34 | 115.9 | 118.88 |
| INDONESIA | 109.75 | 110.5 | 110.95 |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsConsumerPriceIndexRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi")
    field: float | None = Field(default=None, alias="(January, Ferbruary, .., December)")
    tahun: str | None = Field(default=None, alias="Tahun")
    38_province: str | None = Field(default=None, alias="38 Province (2022=100)")
    prov_aceh: str | None = Field(default=None, alias="PROV ACEH")
    prov_sumatera_utara: str | None = Field(default=None, alias="PROV SUMATERA UTARA")
    prov_sumatera_barat: str | None = Field(default=None, alias="PROV SUMATERA BARAT")
    prov_riau: str | None = Field(default=None, alias="PROV RIAU")
    prov_jambi: str | None = Field(default=None, alias="PROV JAMBI")
    prov_sumatera_selatan: str | None = Field(default=None, alias="PROV SUMATERA SELATAN")
    prov_bengkulu: str | None = Field(default=None, alias="PROV BENGKULU")
    prov_lampung: str | None = Field(default=None, alias="PROV LAMPUNG")
    prov_kepulauan_bangka_belitung: str | None = Field(default=None, alias="PROV KEPULAUAN BANGKA BELITUNG")
    prov_kepulauan_riau: str | None = Field(default=None, alias="PROV KEPULAUAN RIAU")
    prov_dki_jakarta: str | None = Field(default=None, alias="PROV DKI JAKARTA")
    prov_jawa_barat: str | None = Field(default=None, alias="PROV JAWA BARAT")
    prov_jawa_tengah: str | None = Field(default=None, alias="PROV JAWA TENGAH")
    prov_di_yogyakarta: str | None = Field(default=None, alias="PROV DI YOGYAKARTA")
    prov_jawa_timur: str | None = Field(default=None, alias="PROV JAWA TIMUR")
    prov_banten: str | None = Field(default=None, alias="PROV BANTEN")
    prov_bali: str | None = Field(default=None, alias="PROV BALI")
    prov_nusa_tenggara_barat: str | None = Field(default=None, alias="PROV NUSA TENGGARA BARAT")
    prov_nusa_tenggara_timur: str | None = Field(default=None, alias="PROV NUSA TENGGARA TIMUR")
    prov_kalimantan_barat: str | None = Field(default=None, alias="PROV KALIMANTAN BARAT")
    prov_kalimantan_tengah: str | None = Field(default=None, alias="PROV KALIMANTAN TENGAH")
    prov_kalimantan_selatan: str | None = Field(default=None, alias="PROV KALIMANTAN SELATAN")
    prov_kalimantan_timur: str | None = Field(default=None, alias="PROV KALIMANTAN TIMUR")
    prov_kalimantan_utara: str | None = Field(default=None, alias="PROV KALIMANTAN UTARA")
    prov_sulawesi_utara: str | None = Field(default=None, alias="PROV SULAWESI UTARA")
    prov_sulawesi_tengah: str | None = Field(default=None, alias="PROV SULAWESI TENGAH")
    prov_sulawesi_selatan: str | None = Field(default=None, alias="PROV SULAWESI SELATAN")
    prov_sulawesi_tenggara: str | None = Field(default=None, alias="PROV SULAWESI TENGGARA")
    prov_gorontalo: str | None = Field(default=None, alias="PROV GORONTALO")
    prov_sulawesi_barat: str | None = Field(default=None, alias="PROV SULAWESI BARAT")
    prov_maluku: str | None = Field(default=None, alias="PROV MALUKU")
    prov_maluku_utara: str | None = Field(default=None, alias="PROV MALUKU UTARA")
    prov_papua_barat: str | None = Field(default=None, alias="PROV PAPUA BARAT")
    prov_papua_barat_daya: str | None = Field(default=None, alias="PROV PAPUA BARAT DAYA")
    prov_papua: str | None = Field(default=None, alias="PROV PAPUA")
    prov_papua_selatan: str | None = Field(default=None, alias="PROV PAPUA SELATAN")
    prov_papua_tengah: str | None = Field(default=None, alias="PROV PAPUA TENGAH")
    prov_papua_pegunungan: str | None = Field(default=None, alias="PROV PAPUA PEGUNUNGAN")
    indonesia: str | None = Field(default=None, alias="INDONESIA")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
