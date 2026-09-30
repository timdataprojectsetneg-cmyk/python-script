# Data Dictionary: Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)`
- Publisher: Mahkamah Agung RI
- Data access: `pdf`
- Update frequency: Daily
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=sXmLNM&nav=MTVfezlBMUQyMjZELTM5N0EtNDkyNC1CQTVGLTc3NzE4QjQ3QUZCN30)
- Target module: `ingestion/usecases/ketenagakerjaan/mahkamah_agung_ri/direktori_putusan_perkara_pengadilan_hubungan/models.py`

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
