# Data Dictionary: BPH Migas – BPH Migas Dorong Optimalisasi Penyaluran BBM Hingga Wilayah Perbatasan Kalimantan Barat

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `BPH Migas – BPH Migas Dorong Optimalisasi Penyaluran BBM Hingga Wilayah Perbatasan Kalimantan Barat`
- Publisher: bphmigas
- Data access: `scraper`
- Update frequency: Berkala
- Eligible: `True`
- Data Dictionary file: [BPH Migas_Penyaluran BBM](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=LeU1M8&nav=MTVfe0MyNzJGMUFDLTIzRjItNEVFRi1BOTRFLTAyREVDRjI4MDc5Nn0)
- Target module: `ingestion/usecases/ketahanan_energi/bphmigas/dorong_optimalisasi_penyaluran_bbm_hingga_wilayah_perbatasan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Titik Pasokan | `titik_pasokan` | String | - | Nama fasilitas yang menjadi sumber pasokan BBM, misalnya Fuel Terminal (S) Sanggau. |
| Wilayah Tujuan | `wilayah_tujuan` | String | - | Wilayah yang menerima atau menjadi tujuan distribusi BBM. |
| Jalur Distribusi | `jalur_distribusi` | String | - | Jalur/infrastruktur yang digunakan dalam distribusi BBM. |
| Skema Pasokan | `skema_pasokan` | String | - | Skema pengelolaan pasokan seperti Reguler, Alternative, dan Emergency (RAE). |
| Potensi Hambatan | `potensi_hambatan` | String | - | Kondisi yang berpotensi menghambat suplai BBM. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class DorongOptimalisasiPenyaluranBbmHinggaWilayahPerbatasanRecord(BaseModel):
    titik_pasokan: str | None = Field(default=None, alias="Titik Pasokan", description="Nama fasilitas yang menjadi sumber pasokan BBM, misalnya Fuel Terminal (S) Sanggau.")
    wilayah_tujuan: str | None = Field(default=None, alias="Wilayah Tujuan", description="Wilayah yang menerima atau menjadi tujuan distribusi BBM.")
    jalur_distribusi: str | None = Field(default=None, alias="Jalur Distribusi", description="Jalur/infrastruktur yang digunakan dalam distribusi BBM.")
    skema_pasokan: str | None = Field(default=None, alias="Skema Pasokan", description="Skema pengelolaan pasokan seperti Reguler, Alternative, dan Emergency (RAE).")
    potensi_hambatan: str | None = Field(default=None, alias="Potensi Hambatan", description="Kondisi yang berpotensi menghambat suplai BBM.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
