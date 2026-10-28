# Data Dictionary: PMA Negara Asal

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `PMA Negara Asal`
- Publisher: BKPM
- Data access: `pdf`
- Update frequency: Triwulanan dan tahunan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/bkpm/pma_negara_asal/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | String | - | 2025-Q4 = Oktober–Desember; 2025-YTD06 = Januari–Juni (Semester I); 2025-YTD09 = Januari–September; 2025-FY = Januari–Desember. |
| Peringkat | `peringkat` | Integer | Urutan | Urutan lima besar pada infografis. |
| Negara Asal | `negara_asal` | String | - | Negara/ekonomi asal PMA sebagaimana sumber. |
| Realisasi PMA | `realisasi_pma` | Decimal | Miliar USD | Nilai realisasi investasi asing, satu desimal sesuai infografis. |
| Halaman PDF | `halaman_pdf` | Integer | Halaman | Nomor halaman PDF sebagai jejak verifikasi. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PmaNegaraAsalRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="2025-Q4 = Oktober–Desember; 2025-YTD06 = Januari–Juni (Semester I); 2025-YTD09 = Januari–September; 2025-FY = Januari–Desember.")
    peringkat: int | None = Field(default=None, alias="Peringkat", description="Urutan lima besar pada infografis.")
    negara_asal: str | None = Field(default=None, alias="Negara Asal", description="Negara/ekonomi asal PMA sebagaimana sumber.")
    realisasi_pma: float | None = Field(default=None, alias="Realisasi PMA", description="Nilai realisasi investasi asing, satu desimal sesuai infografis.")
    halaman_pdf: int | None = Field(default=None, alias="Halaman PDF", description="Nomor halaman PDF sebagai jejak verifikasi.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
