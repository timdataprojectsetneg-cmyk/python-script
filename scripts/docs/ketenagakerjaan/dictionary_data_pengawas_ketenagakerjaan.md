# Data Dictionary: Data Pengawas Ketenagakerjaan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Data Pengawas Ketenagakerjaan`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Quarterly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Data Pengawas Ketenagakerjaan](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=KTxgAr&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0xMzAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/data_pengawas_ketenagakerjaan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String | - | Nama provinsi ("Jumlah" = nasional). |
| Ahli_Pertama | `ahli_pertama` | Integer | Orang | Pengawas jenjang Ahli Pertama. |
| Ahli_Muda | `ahli_muda` | Integer | Orang | Pengawas jenjang Ahli Muda. |
| Ahli_Madya | `ahli_madya` | Integer | Orang | Pengawas jenjang Ahli Madya. |
| Ahli_Utama | `ahli_utama` | Integer | Orang | Pengawas jenjang Ahli Utama. |
| Jumlah | `jumlah` | Integer | Orang | Total pengawas ketenagakerjaan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class DataPengawasKetenagakerjaanRecord(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (\"Jumlah\" = nasional).")
    ahli_pertama: int | None = Field(default=None, alias="Ahli_Pertama", description="Pengawas jenjang Ahli Pertama.")
    ahli_muda: int | None = Field(default=None, alias="Ahli_Muda", description="Pengawas jenjang Ahli Muda.")
    ahli_madya: int | None = Field(default=None, alias="Ahli_Madya", description="Pengawas jenjang Ahli Madya.")
    ahli_utama: int | None = Field(default=None, alias="Ahli_Utama", description="Pengawas jenjang Ahli Utama.")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total pengawas ketenagakerjaan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
