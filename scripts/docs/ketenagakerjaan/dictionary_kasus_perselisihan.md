# Data Dictionary: Kasus Perselisihan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Kasus Perselisihan`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Kasus Perselisihan](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=VMgafF&nav=MTVfe0YxNzJBNUE3LTA2M0EtNEM2RS05NkJDLTIzRTE5NkE0N0NFRH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/kasus_perselisihan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | String | - | Periode data, kumulatif sejak Januari (contoh: "Januari s.d. Juni 2025"). |
| Jenis_Perselisihan | `jenis_perselisihan` | String | - | Hak / Kepentingan / PHK / Antar Serikat Pekerja. |
| Kasus_Pusat | `kasus_pusat` | Integer | Kasus | Perselisihan tercatat di tingkat pusat. |
| Kasus_Daerah | `kasus_daerah` | Integer | Kasus | Perselisihan tercatat di tingkat daerah. |
| Jumlah_Kasus | `jumlah_kasus` | Integer | Kasus | Jumlah perselisihan yang ditangani mediator. |
| Selesai_Bipartit | `selesai_bipartit` | Integer | Kasus | Diselesaikan melalui bipartit. |
| Mediasi_PB | `mediasi_pb` | Integer | Kasus | Diselesaikan mediasi dengan Perjanjian Bersama. |
| Mediasi_Anjuran | `mediasi_anjuran` | Integer | Kasus | Diselesaikan mediasi dengan anjuran mediator. |
| Selesai_Konsiliasi | `selesai_konsiliasi` | Integer | Kasus | Diselesaikan melalui konsiliasi. |
| Selesai_Arbitrase | `selesai_arbitrase` | Integer | Kasus | Diselesaikan melalui arbitrase. |
| Hakim_HI | `hakim_hi` | Integer | Kasus | Diselesaikan melalui Pengadilan Hubungan Industrial. |
| Jumlah_Selesai | `jumlah_selesai` | Integer | Kasus | Total kasus yang telah diselesaikan. |
| Sisa_Kasus | `sisa_kasus` | Integer | Kasus | Kasus yang belum selesai. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KasusPerselisihanRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Periode data, kumulatif sejak Januari (contoh: \"Januari s.d. Juni 2025\").")
    jenis_perselisihan: str | None = Field(default=None, alias="Jenis_Perselisihan", description="Hak / Kepentingan / PHK / Antar Serikat Pekerja.")
    kasus_pusat: int | None = Field(default=None, alias="Kasus_Pusat", description="Perselisihan tercatat di tingkat pusat.")
    kasus_daerah: int | None = Field(default=None, alias="Kasus_Daerah", description="Perselisihan tercatat di tingkat daerah.")
    jumlah_kasus: int | None = Field(default=None, alias="Jumlah_Kasus", description="Jumlah perselisihan yang ditangani mediator.")
    selesai_bipartit: int | None = Field(default=None, alias="Selesai_Bipartit", description="Diselesaikan melalui bipartit.")
    mediasi_pb: int | None = Field(default=None, alias="Mediasi_PB", description="Diselesaikan mediasi dengan Perjanjian Bersama.")
    mediasi_anjuran: int | None = Field(default=None, alias="Mediasi_Anjuran", description="Diselesaikan mediasi dengan anjuran mediator.")
    selesai_konsiliasi: int | None = Field(default=None, alias="Selesai_Konsiliasi", description="Diselesaikan melalui konsiliasi.")
    selesai_arbitrase: int | None = Field(default=None, alias="Selesai_Arbitrase", description="Diselesaikan melalui arbitrase.")
    hakim_hi: int | None = Field(default=None, alias="Hakim_HI", description="Diselesaikan melalui Pengadilan Hubungan Industrial.")
    jumlah_selesai: int | None = Field(default=None, alias="Jumlah_Selesai", description="Total kasus yang telah diselesaikan.")
    sisa_kasus: int | None = Field(default=None, alias="Sisa_Kasus", description="Kasus yang belum selesai.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
