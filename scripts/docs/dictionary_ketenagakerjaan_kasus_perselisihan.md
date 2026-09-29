# Data Dictionary: Kasus Perselisihan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Kasus Perselisihan`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=VMgafF&nav=MTVfe0YxNzJBNUE3LTA2M0EtNEM2RS05NkJDLTIzRTE5NkE0N0NFRH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kasus_perselisihan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Jenis_Perselisihan | `jenis_perselisihan` | String | - | Perselisihan Hak / Kepentingan / PHK / Serikat Pekerja. |
| Jumlah_Pusat | `jumlah_pusat` | Integer | Kasus | Jumlah perselisihan tercatat di tingkat pusat. |
| Jumlah_Daerah | `jumlah_daerah` | Integer | Kasus | Jumlah perselisihan tercatat di tingkat daerah. |
| Bipartit/Mediasi_PB/Mediasi_Anjuran/Konsiliasi/Arbitrasi/Hakim_HI | `bipartit_mediasi_pb_mediasi_anjuran_konsiliasi_arbitrasi_hakim_hi` | Integer | Kasus | Jumlah kasus diselesaikan per mekanisme. |
| Sisa_Kasus | `sisa_kasus` | Integer | Kasus | Kasus belum terselesaikan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KasusPerselisihanRecord(BaseModel):
    jenis_perselisihan: str | None = Field(default=None, alias="Jenis_Perselisihan")
    jumlah_pusat: int | None = Field(default=None, alias="Jumlah_Pusat")
    jumlah_daerah: int | None = Field(default=None, alias="Jumlah_Daerah")
    bipartit_mediasi_pb_mediasi_anjuran_konsiliasi_arbitrasi_hakim_hi: int | None = Field(default=None, alias="Bipartit/Mediasi_PB/Mediasi_Anjuran/Konsiliasi/Arbitrasi/Hakim_HI")
    sisa_kasus: int | None = Field(default=None, alias="Sisa_Kasus")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
