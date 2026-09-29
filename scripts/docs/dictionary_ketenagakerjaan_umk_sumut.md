# Data Dictionary: UMK Sumut

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `Ketenagakerjaan`
- Source: `UMK Sumut`
- Publisher: GoodStats
- Data access: `scraper`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=eIP4mY&nav=MTVfezM3MTMyREZBLTdCNDAtNDQ4MS05MjE1LTc3MEQ5REU2ODM3NH0)
- Target module: `ingestion/usecases/ketenagakerjaan/umk_sumut/models.py`

## Fields

| Label | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|
| Kabupaten Kota | String | - | Nama Kabupaten Kota |
| umk | Integer | Rupiah | Jumlah UMK |
| tahun | Integer | Tahun | Tahun Perhitungan |
| Sample Data | - | - | - |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class UmkSumutRecord(BaseModel):
    kabupaten_kota: str | None = Field(default=None, alias="Kabupaten Kota")
    umk: int | None = Field(default=None, alias="umk")
    tahun: int | None = Field(default=None, alias="tahun")
    sample_data: str | None = Field(default=None, alias="Sample Data")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
