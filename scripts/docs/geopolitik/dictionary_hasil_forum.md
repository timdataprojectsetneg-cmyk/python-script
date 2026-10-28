# Data Dictionary: Hasil Forum ASEAN

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Hasil Forum ASEAN`
- Publisher: ASEAN
- Data access: `pdf`
- Update frequency: Sesuai penyelenggaraan forum
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Diplomasi Multilateral dan Komitmen Internasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/asean/hasil_forum/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tanggal Forum | `tanggal_forum` | Date | Tanggal | Tanggal KTT ASEAN ke-46. |
| Forum | `forum` | String | - | Forum penerbit pernyataan. |
| Paragraf | `paragraf` | Integer | Nomor | Nomor paragraf dokumen sumber. |
| Isu | `isu` | String | - | Topik yang dibahas. |
| Hasil/Sikap Bersama | `hasil_sikap_bersama` | String | - | Parafrasa singkat hasil, komitmen atau seruan dalam pernyataan. |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class HasilForumAseanRecord(BaseModel):
    tanggal_forum: date | None = Field(default=None, alias="Tanggal Forum", description="Tanggal KTT ASEAN ke-46.")
    forum: str | None = Field(default=None, alias="Forum", description="Forum penerbit pernyataan.")
    paragraf: int | None = Field(default=None, alias="Paragraf", description="Nomor paragraf dokumen sumber.")
    isu: str | None = Field(default=None, alias="Isu", description="Topik yang dibahas.")
    hasil_sikap_bersama: str | None = Field(default=None, alias="Hasil/Sikap Bersama", description="Parafrasa singkat hasil, komitmen atau seruan dalam pernyataan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
