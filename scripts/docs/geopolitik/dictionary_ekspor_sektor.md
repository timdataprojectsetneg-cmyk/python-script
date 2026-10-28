# Data Dictionary: Ekspor Sektor Kemendag

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Ekspor Sektor Kemendag`
- Publisher: Kemendag
- Data access: `scraper`
- Update frequency: Bulanan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/kemendag/ekspor_sektor/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | String | YYYY-MM | Bulan observasi. |
| Total Ekspor | `total_ekspor` | Decimal | Juta USD | Total ekspor migas dan nonmigas. |
| Migas | `migas` | Decimal | Juta USD | Ekspor minyak dan gas bumi. |
| Nonmigas | `nonmigas` | Decimal | Juta USD | Ekspor di luar migas. |
| Pertanian | `pertanian` | Decimal | Juta USD | Agriculture: pertanian, perikanan, peternakan dan kehutanan. |
| Industri | `industri` | Decimal | Juta USD | Industri pengolahan menurut definisi sumber. |
| Pertambangan | `pertambangan` | Decimal | Juta USD | Batu bara, bijih logam dan tambang lainnya. |
| Lainnya | `lainnya` | Decimal | Juta USD | Nonmigas di luar pertanian, industri dan pertambangan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class EksporSektorKemendagRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Bulan observasi.")
    total_ekspor: float | None = Field(default=None, alias="Total Ekspor", description="Total ekspor migas dan nonmigas.")
    migas: float | None = Field(default=None, alias="Migas", description="Ekspor minyak dan gas bumi.")
    nonmigas: float | None = Field(default=None, alias="Nonmigas", description="Ekspor di luar migas.")
    pertanian: float | None = Field(default=None, alias="Pertanian", description="Agriculture: pertanian, perikanan, peternakan dan kehutanan.")
    industri: float | None = Field(default=None, alias="Industri", description="Industri pengolahan menurut definisi sumber.")
    pertambangan: float | None = Field(default=None, alias="Pertambangan", description="Batu bara, bijih logam dan tambang lainnya.")
    lainnya: float | None = Field(default=None, alias="Lainnya", description="Nonmigas di luar pertanian, industri dan pertambangan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
