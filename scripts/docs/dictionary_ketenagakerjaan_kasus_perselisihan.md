# Data Dictionary: Kasus Perselisihan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Kasus Perselisihan`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=VMgafF&nav=MTVfe0YxNzJBNUE3LTA2M0EtNEM2RS05NkJDLTIzRTE5NkE0N0NFRH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/kasus_perselisihan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Jenis_Perselisihan | `jenis_perselisihan` | String | - | Perselisihan Hak / Kepentingan / PHK / Serikat Pekerja. |
| Jumlah_Pusat | `jumlah_pusat` | Integer | Kasus | Jumlah perselisihan tercatat di tingkat pusat. |
| Jumlah_Daerah | `jumlah_daerah` | Integer | Kasus | Jumlah perselisihan tercatat di tingkat daerah. |
| Bipartit | `bipartit` | Integer | Kasus | Jumlah kasus diselesaikan per mekanisme. |
| Mediasi_PB | `mediasi_pb` | Integer | Kasus | Jumlah kasus diselesaikan per mekanisme. |
| Mediasi_Anjuran | `mediasi_anjuran` | Integer | Kasus | Jumlah kasus diselesaikan per mekanisme. |
| Konsiliasi | `konsiliasi` | Integer | Kasus | Jumlah kasus diselesaikan per mekanisme. |
| Arbitrasi | `arbitrasi` | Integer | Kasus | Jumlah kasus diselesaikan per mekanisme. |
| Hakim_HI | `hakim_hi` | Integer | Kasus | Jumlah kasus diselesaikan per mekanisme. |
| Sisa_Kasus | `sisa_kasus` | Integer | Kasus | Kasus belum terselesaikan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KasusPerselisihanRecord(BaseModel):
    jenis_perselisihan: str | None = Field(default=None, alias="Jenis_Perselisihan", description="Perselisihan Hak / Kepentingan / PHK / Serikat Pekerja.")
    jumlah_pusat: int | None = Field(default=None, alias="Jumlah_Pusat", description="Jumlah perselisihan tercatat di tingkat pusat.")
    jumlah_daerah: int | None = Field(default=None, alias="Jumlah_Daerah", description="Jumlah perselisihan tercatat di tingkat daerah.")
    bipartit: int | None = Field(default=None, alias="Bipartit", description="Jumlah kasus diselesaikan per mekanisme.")
    mediasi_pb: int | None = Field(default=None, alias="Mediasi_PB", description="Jumlah kasus diselesaikan per mekanisme.")
    mediasi_anjuran: int | None = Field(default=None, alias="Mediasi_Anjuran", description="Jumlah kasus diselesaikan per mekanisme.")
    konsiliasi: int | None = Field(default=None, alias="Konsiliasi", description="Jumlah kasus diselesaikan per mekanisme.")
    arbitrasi: int | None = Field(default=None, alias="Arbitrasi", description="Jumlah kasus diselesaikan per mekanisme.")
    hakim_hi: int | None = Field(default=None, alias="Hakim_HI", description="Jumlah kasus diselesaikan per mekanisme.")
    sisa_kasus: int | None = Field(default=None, alias="Sisa_Kasus", description="Kasus belum terselesaikan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
