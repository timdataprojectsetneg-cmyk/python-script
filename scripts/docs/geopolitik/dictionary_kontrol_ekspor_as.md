# Data Dictionary: Kontrol Ekspor AS

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Kontrol Ekspor AS`
- Publisher: Federal Register
- Data access: `api`
- Update frequency: Harian (hari kerja)
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/federal_register/kontrol_ekspor_as/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| title | `title` | String | - | Judul aturan di Federal Register, mis. "Revisions to the Entity List". Dipakai sebagai judul kebijakan pembatasan dagang/kontrol ekspor AS. |
| publication_date | `publication_date` | Date | Tanggal | Tanggal terbit di Federal Register. Dipakai sebagai tanggal kejadian & filter periode. |
| effective_on | `effective_on` | Date | Tanggal | Tanggal aturan mulai berlaku. Bisa null (mis. dokumen koreksi) dan bisa lebih awal dari publication_date (berlaku surut). |
| html_url | `html_url` | String | URL | Tautan halaman dokumen. Memuat nomor dokumen (mis. 2026-17231); awalan "C1-" = dokumen koreksi atas aturan sebelumnya. |
| document_number* | `document_number` | String | Kode | Turunan dari html_url (segmen ke-4). Kunci dedup; dokumen koreksi (C1-…) ditautkan ke dokumen asalnya. |
| is_correction* | `is_correction` | Boolean | - | Turunan: True bila document_number berawalan "C1-". Koreksi tidak dihitung sebagai aturan baru. |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class KontrolEksporAsRecord(BaseModel):
    title: str | None = Field(default=None, alias="title", description="Judul aturan di Federal Register, mis. \"Revisions to the Entity List\". Dipakai sebagai judul kebijakan pembatasan dagang/kontrol ekspor AS.")
    publication_date: date | None = Field(default=None, alias="publication_date", description="Tanggal terbit di Federal Register. Dipakai sebagai tanggal kejadian & filter periode.")
    effective_on: date | None = Field(default=None, alias="effective_on", description="Tanggal aturan mulai berlaku. Bisa null (mis. dokumen koreksi) dan bisa lebih awal dari publication_date (berlaku surut).")
    html_url: str | None = Field(default=None, alias="html_url", description="Tautan halaman dokumen. Memuat nomor dokumen (mis. 2026-17231); awalan \"C1-\" = dokumen koreksi atas aturan sebelumnya.")
    document_number: str | None = Field(default=None, alias="document_number*", description="Turunan dari html_url (segmen ke-4). Kunci dedup; dokumen koreksi (C1-…) ditautkan ke dokumen asalnya.")
    is_correction: bool | None = Field(default=None, alias="is_correction*", description="Turunan: True bila document_number berawalan \"C1-\". Koreksi tidak dihitung sebagai aturan baru.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
