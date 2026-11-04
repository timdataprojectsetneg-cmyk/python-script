# Data Dictionary: Tabel 48 Unplanned Shutdown (>2 hari) pada Kegiatan Usaha Hulu Migas 
Tahun 2025 

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Tabel 48 Unplanned Shutdown (>2 hari) pada Kegiatan Usaha Hulu Migas 
Tahun 2025 `
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Gangguan HuluHilir](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=OLd2P7&nav=MTVfezM2MkFDQjMzLUVENjYtNDVDOS04NDA3LUE5MzY5REZDMTIxNn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/unplanned_shutdown_pada_kegiatan_usaha_hulu_migas_tahun_2025/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| no | `no` | Integer | - | Nomor urut baris tabel |
| nama_perusahaan | `nama_perusahaan` | String | - | Nama perusahaan kegiatan usaha hulu migas |
| tanggal_kejadian | `tanggal_kejadian` | Date | YYYY-MM-DD | Tanggal kejadian unplanned shutdown |
| penyebab | `penyebab` | String | - | Penyebab unplanned shutdown |

## Generated Pydantic model

```python
from datetime import date as DateType
from pydantic import BaseModel, Field


class UnplannedShutdownPadaKegiatanUsahaHuluMigasTahun2025Record(BaseModel):
    no: int | None = Field(default=None, alias="no", description="Nomor urut baris tabel")
    nama_perusahaan: str | None = Field(default=None, alias="nama_perusahaan", description="Nama perusahaan kegiatan usaha hulu migas")
    tanggal_kejadian: DateType | None = Field(default=None, alias="tanggal_kejadian", description="Tanggal kejadian unplanned shutdown")
    penyebab: str | None = Field(default=None, alias="penyebab", description="Penyebab unplanned shutdown")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
