# Data Dictionary: Indeks Risiko Geopolitik

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Indeks Risiko Geopolitik`
- Publisher: Caldara & Iacoviello
- Data access: `excel`
- Update frequency: Bulanan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Situasi Global dan Kawasan (1).xlsx
- Target module: `ingestion/usecases/geopolitik/caldara_iacoviello/indeks_risiko_geopolitik/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| month | `month` | String | YYYY-MM | Bulan observasi dalam seri sumber. |
| GPR | `gpr` | Decimal | Indeks | Indeks risiko geopolitik keseluruhan. |
| GPRT | `gprt` | Decimal | Indeks | Komponen ancaman geopolitik. |
| GPRA | `gpra` | Decimal | Indeks | Komponen aksi/peristiwa geopolitik. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class IndeksRisikoGeopolitikRecord(BaseModel):
    month: str | None = Field(default=None, alias="month", description="Bulan observasi dalam seri sumber.")
    gpr: float | None = Field(default=None, alias="GPR", description="Indeks risiko geopolitik keseluruhan.")
    gprt: float | None = Field(default=None, alias="GPRT", description="Komponen ancaman geopolitik.")
    gpra: float | None = Field(default=None, alias="GPRA", description="Komponen aksi/peristiwa geopolitik.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
