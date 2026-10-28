# Data Dictionary: Agenda Forum ASEAN

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Agenda Forum ASEAN`
- Publisher: ASEAN
- Data access: `pdf`
- Update frequency: Sesuai revisi kalender
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Diplomasi Multilateral dan Komitmen Internasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/asean/agenda_forum/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Nomor pada Kalender | `nomor_pada_kalender` | Integer | Nomor | Nomor kegiatan asli untuk menemukan record. |
| Pertemuan | `pertemuan` | String | - | Nama kegiatan diringkas dari kalender. |
| Jadwal menurut Sumber | `jadwal_menurut_sumber` | String | - | Rentang/jadwal indikatif. Tidak dipaksakan menjadi tanggal pasti. |
| Lokasi menurut Sumber | `lokasi_menurut_sumber` | String | - | Lokasi atau TBC (to be confirmed). |
| Pilar | `pilar` | String | Kode | AEC = ekonomi; APSC = politik-keamanan; ASCC = sosial-budaya. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class AgendaForumAseanRecord(BaseModel):
    nomor_pada_kalender: int | None = Field(default=None, alias="Nomor pada Kalender", description="Nomor kegiatan asli untuk menemukan record.")
    pertemuan: str | None = Field(default=None, alias="Pertemuan", description="Nama kegiatan diringkas dari kalender.")
    jadwal_menurut_sumber: str | None = Field(default=None, alias="Jadwal menurut Sumber", description="Rentang/jadwal indikatif. Tidak dipaksakan menjadi tanggal pasti.")
    lokasi_menurut_sumber: str | None = Field(default=None, alias="Lokasi menurut Sumber", description="Lokasi atau TBC (to be confirmed).")
    pilar: str | None = Field(default=None, alias="Pilar", description="AEC = ekonomi; APSC = politik-keamanan; ASCC = sosial-budaya.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
