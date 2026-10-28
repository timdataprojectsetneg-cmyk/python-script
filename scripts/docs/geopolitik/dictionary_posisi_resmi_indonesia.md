# Data Dictionary: Posisi Resmi Indonesia

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Posisi Resmi Indonesia`
- Publisher: Setpres
- Data access: `scraper`
- Update frequency: Sesuai pernyataan resmi
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/setpres/posisi_resmi_indonesia/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tanggal Pernyataan | `tanggal_pernyataan` | Date | Tanggal | Tanggal pernyataan pers. |
| Pejabat | `pejabat` | String | - | Penyampai posisi resmi. |
| Forum/Konteks | `forum_konteks` | String | - | Konteks pernyataan. |
| Isu | `isu` | String | - | Isu yang dipisahkan dari isi pidato. |
| Posisi yang Dinyatakan | `posisi_yang_dinyatakan` | String | - | Parafrasa ringkas posisi, tanpa inferensi sentimen. |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class PosisiResmiIndonesiaRecord(BaseModel):
    tanggal_pernyataan: date | None = Field(default=None, alias="Tanggal Pernyataan", description="Tanggal pernyataan pers.")
    pejabat: str | None = Field(default=None, alias="Pejabat", description="Penyampai posisi resmi.")
    forum_konteks: str | None = Field(default=None, alias="Forum/Konteks", description="Konteks pernyataan.")
    isu: str | None = Field(default=None, alias="Isu", description="Isu yang dipisahkan dari isi pidato.")
    posisi_yang_dinyatakan: str | None = Field(default=None, alias="Posisi yang Dinyatakan", description="Parafrasa ringkas posisi, tanpa inferensi sentimen.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
