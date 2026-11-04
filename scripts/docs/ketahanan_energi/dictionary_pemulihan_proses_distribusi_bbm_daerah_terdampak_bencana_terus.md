# Data Dictionary: BPH Migas – Pemulihan Proses Distribusi BBM Daerah Terdampak Bencana Terus Dilakukan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `BPH Migas – Pemulihan Proses Distribusi BBM Daerah Terdampak Bencana Terus Dilakukan`
- Publisher: bphmigas
- Data access: `scraper`
- Update frequency: Berkala
- Eligible: `True`
- Data Dictionary file: [BPH Migas_Gangguan Distribusi](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=sJsYPT&nav=MTVfezMwQ0EzMDUzLTE0NDUtNDMwMy04N0QwLTA0Q0MzQ0I0QzRDMH0)
- Target module: `ingestion/usecases/ketahanan_energi/bphmigas/pemulihan_proses_distribusi_bbm_daerah_terdampak_bencana_terus/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Wilayah Tujuan | `wilayah_tujuan` | String | - | Wilayah yang menerima pasokan BBM. |
| Titik Pasokan Utama | `titik_pasokan_utama` | String | - | Fuel Terminal atau terminal yang menjadi sumber pasokan sebelum terjadi gangguan. |
| Titik Pasokan Alternatif | `titik_pasokan_alternatif` | String | - | Fuel Terminal atau titik pasokan yang digunakan sebagai alternatif ketika pasokan utama terganggu. |
| Skema Pasokan | `skema_pasokan` | String | - | Mekanisme pasokan alternatif atau darurat yang digunakan. |
| Kondisi Gangguan | `kondisi_gangguan` | String | - | Kondisi yang menyebabkan perubahan titik pasokan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PemulihanProsesDistribusiBbmDaerahTerdampakBencanaTerusRecord(BaseModel):
    wilayah_tujuan: str | None = Field(default=None, alias="Wilayah Tujuan", description="Wilayah yang menerima pasokan BBM.")
    titik_pasokan_utama: str | None = Field(default=None, alias="Titik Pasokan Utama", description="Fuel Terminal atau terminal yang menjadi sumber pasokan sebelum terjadi gangguan.")
    titik_pasokan_alternatif: str | None = Field(default=None, alias="Titik Pasokan Alternatif", description="Fuel Terminal atau titik pasokan yang digunakan sebagai alternatif ketika pasokan utama terganggu.")
    skema_pasokan: str | None = Field(default=None, alias="Skema Pasokan", description="Mekanisme pasokan alternatif atau darurat yang digunakan.")
    kondisi_gangguan: str | None = Field(default=None, alias="Kondisi Gangguan", description="Kondisi yang menyebabkan perubahan titik pasokan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
