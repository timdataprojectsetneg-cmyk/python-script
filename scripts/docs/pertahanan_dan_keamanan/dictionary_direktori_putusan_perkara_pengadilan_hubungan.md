# Data Dictionary: Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `pertahanan_dan_keamanan`
- Source: `Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)`
- Publisher: MA RI
- Data access: `scraper`
- Update frequency: Daily
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx
- Target module: `ingestion/usecases/pertahanan_dan_keamanan/ma_ri/direktori_putusan_perkara_pengadilan_hubungan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| - | - | - | - | No fields parsed from the Data Dictionary. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class DirektoriPutusanPerkaraPengadilanHubunganRecord(BaseModel):

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
