# Data Dictionary: Harga Komoditas Dunia

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Harga Komoditas Dunia`
- Publisher: World Bank
- Data access: `excel`
- Update frequency: Bulanan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/world_bank/harga_komoditas_dunia/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | String | YYYY-MM | Bulan pada Monthly Prices; format YYYY M MM dinormalisasi menjadi YYYY-MM. |
| Komoditas | `komoditas` | String | - | Nama kolom komoditas asli. |
| Harga | `harga` | Decimal | Mengikuti satuan | Harga bulanan nominal. Missing value tetap kosong. |
| Satuan | `satuan` | String | - | Unit persis dari baris satuan sumber. $ = USD; mt = metric ton; bbl = barrel; mmbtu = million BTU. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class HargaKomoditasDuniaRecord(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Bulan pada Monthly Prices; format YYYY M MM dinormalisasi menjadi YYYY-MM.")
    komoditas: str | None = Field(default=None, alias="Komoditas", description="Nama kolom komoditas asli.")
    harga: float | None = Field(default=None, alias="Harga", description="Harga bulanan nominal. Missing value tetap kosong.")
    satuan: str | None = Field(default=None, alias="Satuan", description="Unit persis dari baris satuan sumber. $ = USD; mt = metric ton; bbl = barrel; mmbtu = million BTU.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
