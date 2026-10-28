# Data Dictionary: Keanggotaan Forum

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Keanggotaan Forum`
- Publisher: World Bank
- Data access: `scraper`
- Update frequency: Sesuai perubahan keanggotaan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Diplomasi Multilateral dan Komitmen Internasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/world_bank/keanggotaan_forum/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Organisasi/Forum | `organisasi_forum` | String | - | Nama organisasi atau forum. |
| Status/Peran | `status_peran` | String | - | Status yang disebut dalam sumber primer. |
| Tanggal/Tahun/Periode | `tanggal_tahun_periode` | String | - | Tanggal masuk, tahun, atau periode peran sesuai ketelitian sumber; tidak diisi tanggal fiktif. |
| Keterangan Periode | `keterangan_periode` | String | - | Menjelaskan makna periode dan sejarah bila relevan. |
| URL Sumber | `url_sumber` | String | URL | Daftar anggota atau pernyataan resmi. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KeanggotaanForumRecord(BaseModel):
    organisasi_forum: str | None = Field(default=None, alias="Organisasi/Forum", description="Nama organisasi atau forum.")
    status_peran: str | None = Field(default=None, alias="Status/Peran", description="Status yang disebut dalam sumber primer.")
    tanggal_tahun_periode: str | None = Field(default=None, alias="Tanggal/Tahun/Periode", description="Tanggal masuk, tahun, atau periode peran sesuai ketelitian sumber; tidak diisi tanggal fiktif.")
    keterangan_periode: str | None = Field(default=None, alias="Keterangan Periode", description="Menjelaskan makna periode dan sejarah bila relevan.")
    url_sumber: str | None = Field(default=None, alias="URL Sumber", description="Daftar anggota atau pernyataan resmi.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
