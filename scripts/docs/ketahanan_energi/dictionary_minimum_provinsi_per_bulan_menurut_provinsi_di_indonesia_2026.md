# Data Dictionary: BPS Provinsi Jawa Tengah - Upah Minimum Provinsi (UMP) per Bulan Menurut Provinsi di Indonesia (rupiah) 2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `BPS Provinsi Jawa Tengah - Upah Minimum Provinsi (UMP) per Bulan Menurut Provinsi di Indonesia (rupiah) 2026`
- Publisher: bps
- Data access: `excel`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [BPS - Statistik UMP 2026](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=92daYK&nav=MTVfezE2NjAyODYzLTQ1RDAtNEQ2RS05OTIzLTA2NjdBRjQyNzgxNX0)
- Target module: `ingestion/usecases/ketahanan_energi/bps/minimum_provinsi_per_bulan_menurut_provinsi_di_indonesia_2026/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | Text | provinsi | Nama provinsi. |
| UMP 2026 | `ump_2026` | Decimal | Rp/bulan | Upah Minimum Provinsi tahun 2026. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class MinimumProvinsiPerBulanMenurutProvinsiDiIndonesia2026Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi.")
    ump_2026: float | None = Field(default=None, alias="UMP 2026", description="Upah Minimum Provinsi tahun 2026.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
