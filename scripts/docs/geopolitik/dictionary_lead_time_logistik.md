# Data Dictionary: Lead Time Logistik Indonesia

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Lead Time Logistik Indonesia`
- Publisher: World Bank
- Data access: `api`
- Update frequency: Survei berkala; tidak tahunan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/world_bank/lead_time_logistik/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| indicator_code | `indicator_code` | String | Kode | Kode indikator World Bank. |
| indicator_name | `indicator_name` | String | - | Nama ukuran lead time. |
| year | `year` | Integer | Tahun | Tahun observasi yang memiliki nilai. |
| value | `value` | Decimal | Hari | Median lead time menurut survei. |
| unit | `unit` | String | - | Satuan nilai. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class LeadTimeLogistikIndonesiaRecord(BaseModel):
    indicator_code: str | None = Field(default=None, alias="indicator_code", description="Kode indikator World Bank.")
    indicator_name: str | None = Field(default=None, alias="indicator_name", description="Nama ukuran lead time.")
    year: int | None = Field(default=None, alias="year", description="Tahun observasi yang memiliki nilai.")
    value: float | None = Field(default=None, alias="value", description="Median lead time menurut survei.")
    unit: str | None = Field(default=None, alias="unit", description="Satuan nilai.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
