# Data Dictionary: LAKIN Ditjen Migas 2025_Tabel 49 Unplanned Shutdown pada Kegiatan Usaha Hulu Migas 

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `LAKIN Ditjen Migas 2025_Tabel 49 Unplanned Shutdown pada Kegiatan Usaha Hulu Migas `
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Frek Gangguan](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=fNOPN2&nav=MTVfezc5MDUyQzQ5LTlBQjEtNDU1Qi05QjYwLTVBODAwMjZGRTA2M30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/migas_2025_tabel_49_unplanned_shutdown_pada_kegiatan_usaha/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| jumlah_unplanned_shutdown | `jumlah_unplanned_shutdown` | Integer | Kejadian | Jumlah unplanned shutdown kegiatan usaha hulu migas per tahun |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class Migas2025Tabel49UnplannedShutdownPadaKegiatanUsahaRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    jumlah_unplanned_shutdown: int | None = Field(default=None, alias="jumlah_unplanned_shutdown", description="Jumlah unplanned shutdown kegiatan usaha hulu migas per tahun")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
