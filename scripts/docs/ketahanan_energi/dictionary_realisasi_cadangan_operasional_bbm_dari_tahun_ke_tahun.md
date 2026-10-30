# Data Dictionary: Tabel 16 Realisasi Cadangan Operasional BBM dari Tahun ke Tahun 

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel 16 Realisasi Cadangan Operasional BBM dari Tahun ke Tahun `
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Cadangan Operasional](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=IxHdXO&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wMTAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/realisasi_cadangan_operasional_bbm_dari_tahun_ke_tahun/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| jenis_cadangan | `jenis_cadangan` | Categorical | - | Jenis cadangan operasional: BBM atau LPG |
| nilai | `nilai` | Numeric (Decimal) | hari | Cadangan operasional per jenis dan tahun |
| satuan | `satuan` | Categorical | - | hari |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class RealisasiCadanganOperasionalBbmDariTahunKeTahunRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    jenis_cadangan: str | None = Field(default=None, alias="jenis_cadangan", description="Jenis cadangan operasional: BBM atau LPG")
    nilai: str | None = Field(default=None, alias="nilai", description="Cadangan operasional per jenis dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="hari")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
