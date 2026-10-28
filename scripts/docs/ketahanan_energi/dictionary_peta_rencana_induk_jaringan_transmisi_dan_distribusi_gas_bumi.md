# Data Dictionary: Gambar 25 Peta Rencana Induk Jaringan Transmisi dan Distribusi gas Bumi 
Nasional (RIJTDGBN) 

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Gambar 25 Peta Rencana Induk Jaringan Transmisi dan Distribusi gas Bumi 
Nasional (RIJTDGBN) `
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Ditjen Migas_Peta RIJTDGBN](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=3BI1kc&nav=MTVfe0U1NkJEMkM3LTcyMjMtNDU4Mi05N0QwLTAxNTRFQjIzOTA4NX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/peta_rencana_induk_jaringan_transmisi_dan_distribusi_gas_bumi/models.py`

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


class PetaRencanaIndukJaringanTransmisiDanDistribusiGasBumiRecord(BaseModel):
    tanggal_publikasi: date | None = Field(default=None, alias="tanggal_publikasi", description="Tanggal artikel terbit")
    nama_pipa: str | None = Field(default=None, alias="nama_pipa", description="Nama pipa transmisi gas bumi")
    titik_awal: str | None = Field(default=None, alias="titik_awal", description="Titik awal pipa (dari nama pipa)")
    titik_akhir: str | None = Field(default=None, alias="titik_akhir", description="Titik akhir pipa (dari nama pipa)")
    status_pipa: str | None = Field(default=None, alias="status_pipa", description="Status pembangunan sebagaimana disebut artikel")
    sumber: str | None = Field(default=None, alias="sumber", description="Nama sumber dan penyampai")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
