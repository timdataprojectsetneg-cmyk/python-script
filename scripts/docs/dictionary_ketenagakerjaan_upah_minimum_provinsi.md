# Data Dictionary: Upah Minimum Provinsi (UMP)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `Ketenagakerjaan`
- Source: `Upah Minimum Provinsi (UMP)`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=y38ycW&nav=MTVfe0E2ODc2NTVDLTExQzAtNDQ4Qi1BRkQ4LTNDMzk1N0M4Qzk5Q30)
- Target module: `ingestion/usecases/ketenagakerjaan/upah_minimum_provinsi/models.py`

## Fields

| Label | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|
| Provinsi | String | - | Nama provinsi. |
| Nilai_UMP | Decimal | Rupiah | Besaran UMP dalam Rupiah. |
| Added fields for datamart | - | - | - |
| Persentase_Kenaikan_YoY | Decimal | % | (UMP_tahun_ini - UMP_tahun_lalu)/UMP_tahun_lalu x 100%. |
| Tahun | Integer | - | Tahun berlaku UMP. |
| Upah Minimum Provinsi di Indonesia | - | - | - |
| Tahun 2025 | - | - | - |
| No | Provinsi | Upah Minimum (Rp) | - |
| 1 | Aceh | 3.685.616,00 | - |
| 2 | Sumatera Utara | 2.992.559,00 | - |
| 3 | Sumatera Barat | 2.994.193,47 | - |
| 4 | Riau | 3.508.776,22 | - |
| 5 | Jambi | 3.234.535,00 | - |
| 6 | Sumatera Selatan | 3.681.571,00 | - |
| 7 | Bengkulu | 2.670.039,39 | - |
| 8 | Lampung | 2.893.070,00 | - |
| 9 | Bangka Belitung | 3.876.600,00 | - |
| 10 | Kepulauan Riau | 3.623.654,00 | - |
| 11 | DKI Jakarta | 5.396.761,00 | - |
| 12 | Jawa Barat | 2.191.232,18 | - |
| 13 | Jawa Tengah | 2.169.349,00 | - |
| 14 | DI. Yogyakarta | 2.264.080,95 | - |
| 15 | Jawa Timur | 2.305.985,00 | - |
| 16 | Banten | 2.905.119,90 | - |
| 17 | Bali | 2.996.561,00 | - |
| 18 | Nusa Tenggara Barat | 2.602.931,00 | - |
| 19 | Nusa Tenggara Timur | 2.328.969,69 | - |
| 20 | Kalimantan Barat | 2.878.286,00 | - |
| 21 | Kalimantan Tengah | 3.473.621,04 | - |
| 22 | Kalimantan Selatan | 3.496.195,00 | - |
| 23 | Kalimantan Timur | 3.579.313,77 | - |
| 24 | Kalimantan Utara | 3.580.160,00 | - |
| 25 | Sulawesi Utara | 3.775.425,00 | - |
| 26 | Sulawesi Tengah | 2.915.000,00 | - |
| 27 | Sulawesi Selatan | 3.657.527,37 | - |
| 28 | Sulawesi Tenggara | 3.073.551,70 | - |
| 29 | Gorontalo | 3.221.731,00 | - |
| 30 | Sulawesi Barat | 3.104.430,00 | - |
| 31 | Maluku | 3.141.700,00 | - |
| 32 | Maluku Utara | 3.408.000,00 | - |
| 33 | Papua Barat | 3.615.000,00 | - |
| 34 | Papua Barat Daya | 3.614.000,00 | - |
| 35 | Papua | 4.285.850,00 | - |
| 36 | Papua Selatan | 4.285.850,00 | - |
| 37 | Papua Tengah | 4.285.848,00 | - |
| 38 | Papua Pegunungan | 4.285.850,00 | - |
| Rata-Rata | - | 3.315.761,65 | - |
| Sumber: Kemnaker RI | - | - | - |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class UpahMinimumProvinsiRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi")
    nilai_ump: float | None = Field(default=None, alias="Nilai_UMP")
    added_fields_for_datamart: str | None = Field(default=None, alias="Added fields for datamart")
    persentase_kenaikan_yoy: float | None = Field(default=None, alias="Persentase_Kenaikan_YoY")
    tahun: int | None = Field(default=None, alias="Tahun")
    upah_minimum_provinsi_di_indonesia: str | None = Field(default=None, alias="Upah Minimum Provinsi di Indonesia")
    tahun_2025: str | None = Field(default=None, alias="Tahun 2025")
    no: str | None = Field(default=None, alias="No")
    1: str | None = Field(default=None, alias="1")
    2: str | None = Field(default=None, alias="2")
    3: str | None = Field(default=None, alias="3")
    4: str | None = Field(default=None, alias="4")
    5: str | None = Field(default=None, alias="5")
    6: str | None = Field(default=None, alias="6")
    7: str | None = Field(default=None, alias="7")
    8: str | None = Field(default=None, alias="8")
    9: str | None = Field(default=None, alias="9")
    10: str | None = Field(default=None, alias="10")
    11: str | None = Field(default=None, alias="11")
    12: str | None = Field(default=None, alias="12")
    13: str | None = Field(default=None, alias="13")
    14: str | None = Field(default=None, alias="14")
    15: str | None = Field(default=None, alias="15")
    16: str | None = Field(default=None, alias="16")
    17: str | None = Field(default=None, alias="17")
    18: str | None = Field(default=None, alias="18")
    19: str | None = Field(default=None, alias="19")
    20: str | None = Field(default=None, alias="20")
    21: str | None = Field(default=None, alias="21")
    22: str | None = Field(default=None, alias="22")
    23: str | None = Field(default=None, alias="23")
    24: str | None = Field(default=None, alias="24")
    25: str | None = Field(default=None, alias="25")
    26: str | None = Field(default=None, alias="26")
    27: str | None = Field(default=None, alias="27")
    28: str | None = Field(default=None, alias="28")
    29: str | None = Field(default=None, alias="29")
    30: str | None = Field(default=None, alias="30")
    31: str | None = Field(default=None, alias="31")
    32: str | None = Field(default=None, alias="32")
    33: str | None = Field(default=None, alias="33")
    34: str | None = Field(default=None, alias="34")
    35: str | None = Field(default=None, alias="35")
    36: str | None = Field(default=None, alias="36")
    37: str | None = Field(default=None, alias="37")
    38: str | None = Field(default=None, alias="38")
    rata_rata: str | None = Field(default=None, alias="Rata-Rata")
    sumber_kemnaker_ri: str | None = Field(default=None, alias="Sumber: Kemnaker RI")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
