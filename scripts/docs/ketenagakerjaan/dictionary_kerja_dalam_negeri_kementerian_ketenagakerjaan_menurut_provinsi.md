# Data Dictionary: Tabel ID.GBA: Penempatan Kerja: Dalam Negeri: Kementerian Ketenagakerjaan: Menurut Provinsi

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Tabel ID.GBA: Penempatan Kerja: Dalam Negeri: Kementerian Ketenagakerjaan: Menurut Provinsi`
- Publisher: ceicdata
- Data access: `api`
- Update frequency: Tahunan – perlu konfirmasi
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - penempatan_kerja_dalam_negeri_menurut_provinsi](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=gBIugq&nav=MTVfezlENTc4NzU5LTQ4OTctNEYwRS1BNjM1LTJBOUUwQ0Q4M0JBMn0)
- Target module: `ingestion/usecases/ketenagakerjaan/ceicdata/kerja_dalam_negeri_kementerian_ketenagakerjaan_menurut_provinsi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| - | - | - | - | No fields parsed from the Data Dictionary. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KerjaDalamNegeriKementerianKetenagakerjaanMenurutProvinsiRecord(BaseModel):

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
