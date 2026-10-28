# Data Dictionary: Penyalur BBM 47302 Agen Industri PT Pertamina Patra Niaga

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Penyalur BBM 47302 Agen Industri PT Pertamina Patra Niaga`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Per Semester
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Penyalur Agen Pertamina](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=KoI10z&nav=MTVfe0NEQzA2NUIxLUE3OTctNDhCRi05M0U3LUNFODFGOUVGMEVDQ30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/penyalur_bbm_47302_agen_industri_pt_pertamina_patra_niaga/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tanggal_publikasi | `tanggal_publikasi` | Date | YYYY-MM-DD | Tanggal artikel terbit |
| nama_pipa | `nama_pipa` | String | - | Nama pipa transmisi gas bumi |
| titik_awal | `titik_awal` | String | - | Titik awal pipa (dari nama pipa) |
| titik_akhir | `titik_akhir` | String | - | Titik akhir pipa (dari nama pipa) |
| status_pipa | `status_pipa` | String | - | Status pembangunan sebagaimana disebut artikel |
| sumber | `sumber` | String | - | Nama sumber dan penyampai |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class PenyalurBbm47302AgenIndustriPtPertaminaPatraNiagaRecord(BaseModel):
    tanggal_publikasi: date | None = Field(default=None, alias="tanggal_publikasi", description="Tanggal artikel terbit")
    nama_pipa: str | None = Field(default=None, alias="nama_pipa", description="Nama pipa transmisi gas bumi")
    titik_awal: str | None = Field(default=None, alias="titik_awal", description="Titik awal pipa (dari nama pipa)")
    titik_akhir: str | None = Field(default=None, alias="titik_akhir", description="Titik akhir pipa (dari nama pipa)")
    status_pipa: str | None = Field(default=None, alias="status_pipa", description="Status pembangunan sebagaimana disebut artikel")
    sumber: str | None = Field(default=None, alias="sumber", description="Nama sumber dan penyampai")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
