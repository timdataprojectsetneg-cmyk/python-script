# Data Dictionary: Tabel ID.GBA: Pengangguran: Menurut Usia

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Tabel ID.GBA: Pengangguran: Menurut Usia`
- Publisher: ceicdata
- Data access: `api`
- Update frequency: Semesteran (Feb, Agu)
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - pengangguran_menurut_usia](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/1.%20Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan%20(1).xlsx?d=wff0dbd62d68e4b14823be60d69d2b660&csf=1&web=1&e=9cx6BR&nav=MTVfezY0RTQzODgzLTlBRTItNDNEMC1CNkFCLTRCMjVFMDM4QjNGRH0)
- Target module: `ingestion/usecases/ketenagakerjaan/ceicdata/tabel_id_gba_pengangguran_menurut_usia/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| table_id | `table_id` | String | - | Kode tabel CEIC (TBxxxx) sumber data |
| series_id | `series_id` | Integer | - | ID series CEIC |
| series_name | `series_name` | String | - | Nama lengkap series; memuat dimensi seperti provinsi, usia, atau industri |
| unit | `unit` | String | - | Satuan nilai dari metadata CEIC (mis. Person th) |
| frequency | `frequency` | String | - | Frekuensi data (mis. Semiannually, Annual, Monthly) |
| province | `province` | String | - | Provinsi dari metadata series; null bila series nasional |
| date | `date` | Date | - | Periode observasi (YYYY-MM-DD) |
| value | `value` | Float | sesuai unit | Nilai observasi |
| last_update_time | `last_update_time` | Date | - | Tanggal terakhir data diperbarui di CEIC (YYYY-MM-DD) |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class TabelIdGbaPengangguranMenurutUsiaRecord(BaseModel):
    table_id: str | None = Field(default=None, alias="table_id", description="Kode tabel CEIC (TBxxxx) sumber data")
    series_id: int | None = Field(default=None, alias="series_id", description="ID series CEIC")
    series_name: str | None = Field(default=None, alias="series_name", description="Nama lengkap series; memuat dimensi seperti provinsi, usia, atau industri")
    unit: str | None = Field(default=None, alias="unit", description="Satuan nilai dari metadata CEIC (mis. Person th)")
    frequency: str | None = Field(default=None, alias="frequency", description="Frekuensi data (mis. Semiannually, Annual, Monthly)")
    province: str | None = Field(default=None, alias="province", description="Provinsi dari metadata series; null bila series nasional")
    date: date | None = Field(default=None, alias="date", description="Periode observasi (YYYY-MM-DD)")
    value: float | None = Field(default=None, alias="value", description="Nilai observasi")
    last_update_time: date | None = Field(default=None, alias="last_update_time", description="Tanggal terakhir data diperbarui di CEIC (YYYY-MM-DD)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
