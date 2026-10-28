# Data Dictionary: Impor Golongan Kemendag

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Impor Golongan Kemendag`
- Publisher: Kemendag
- Data access: `scraper`
- Update frequency: Bulanan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/kemendag/impor_golongan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | String | YYYY-MM | Bulan observasi. |
| Total Impor | `total_impor` | Decimal | Juta USD | Total impor Indonesia. |
| Barang Konsumsi | `barang_konsumsi` | Decimal | Juta USD | Barang tahan lama/tidak tahan lama untuk konsumsi rumah tangga. |
| Bahan Baku/Penolong | `bahan_baku_penolong` | Decimal | Juta USD | Input dan perlengkapan yang menunjang proses produksi. |
| Barang Modal | `barang_modal` | Decimal | Juta USD | Barang tahan lama untuk kelancaran dan kelangsungan produksi. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class ImporGolonganKemendagRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Bulan observasi.")
    total_impor: float | None = Field(default=None, alias="Total Impor", description="Total impor Indonesia.")
    barang_konsumsi: float | None = Field(default=None, alias="Barang Konsumsi", description="Barang tahan lama/tidak tahan lama untuk konsumsi rumah tangga.")
    bahan_baku_penolong: float | None = Field(default=None, alias="Bahan Baku/Penolong", description="Input dan perlengkapan yang menunjang proses produksi.")
    barang_modal: float | None = Field(default=None, alias="Barang Modal", description="Barang tahan lama untuk kelancaran dan kelangsungan produksi.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
