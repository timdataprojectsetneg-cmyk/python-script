# Data Dictionary: Ekspor Impor Bulanan BPS

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Ekspor Impor Bulanan BPS`
- Publisher: BPS
- Data access: `excel`
- Update frequency: Bulanan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/bps/ekspor_impor_bulanan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | String | YYYY-MM | Bulan observasi perdagangan. |
| Nilai Ekspor | `nilai_ekspor` | Decimal | USD | Nilai ekspor barang Indonesia pada bulan observasi. |
| Berat Ekspor | `berat_ekspor` | Decimal | Kg | Berat bersih ekspor barang pada bulan observasi. |
| Nilai Impor | `nilai_impor` | Decimal | USD | Nilai impor barang Indonesia pada bulan observasi. |
| Berat Impor | `berat_impor` | Decimal | Kg | Berat bersih impor barang pada bulan observasi. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class EksporImporBulananBpsRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Bulan observasi perdagangan.")
    nilai_ekspor: float | None = Field(default=None, alias="Nilai Ekspor", description="Nilai ekspor barang Indonesia pada bulan observasi.")
    berat_ekspor: float | None = Field(default=None, alias="Berat Ekspor", description="Berat bersih ekspor barang pada bulan observasi.")
    nilai_impor: float | None = Field(default=None, alias="Nilai Impor", description="Nilai impor barang Indonesia pada bulan observasi.")
    berat_impor: float | None = Field(default=None, alias="Berat Impor", description="Berat bersih impor barang pada bulan observasi.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
