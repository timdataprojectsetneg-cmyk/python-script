# Data Dictionary: Tabel 18 Jumlah NIK Pengguna LPG 3kg Berdasarkan Kelompok

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel 18 Jumlah NIK Pengguna LPG 3kg Berdasarkan Kelompok`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [LKJ - NIK Pengguna LPG 3kg](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=xJg7UF&nav=MTVfezMyMDU0NUY2LTc4RUMtNDEwNC1CNjMyLURGRjM2NzlEMDg4QX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/jumlah_nik_pengguna_lpg_3kg_berdasarkan_kelompok/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| kelompok | `kelompok` | String | - | Kelompok pengguna: Rumah Tangga, Usaha Mikro, Petani Sasaran, Nelayan Sasaran, Pengecer, atau TOTAL |
| nilai | `nilai` | Float | Juta atau ribu | Jumlah NIK pengguna LPG 3 kg per kelompok |
| satuan | `satuan` | String | - | Juta atau ribu, sesuai baris (tidak dikonversi) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class JumlahNikPenggunaLpg3KgBerdasarkanKelompokRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kelompok: str | None = Field(default=None, alias="kelompok", description="Kelompok pengguna: Rumah Tangga, Usaha Mikro, Petani Sasaran, Nelayan Sasaran, Pengecer, atau TOTAL")
    nilai: float | None = Field(default=None, alias="nilai", description="Jumlah NIK pengguna LPG 3 kg per kelompok")
    satuan: str | None = Field(default=None, alias="satuan", description="Juta atau ribu, sesuai baris (tidak dikonversi)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
