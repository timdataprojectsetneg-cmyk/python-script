# Data Dictionary: BPH Migas – Integrasi RDMP Balikpapan dengan Fuel Terminal Tanjung Batu Tingkatkan Efisiensi dan Ketahanan Energi

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `BPH Migas – Integrasi RDMP Balikpapan dengan Fuel Terminal Tanjung Batu Tingkatkan Efisiensi dan Ketahanan Energi`
- Publisher: bphmigas
- Data access: `scraper`
- Update frequency: Berkala
- Eligible: `True`
- Data Dictionary file: [BPH Migas_Integrasi RDMP](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=edjjwm&nav=MTVfezFEMDNDMDhCLTlGOEEtNDkxRC04QUMxLTgzNTA4RjYzQjQ5NH0)
- Target module: `ingestion/usecases/ketahanan_energi/bphmigas/integrasi_rdmp_balikpapan_dengan_fuel_terminal_tanjung_batu/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Node Asal | `node_asal` | String | - | Fasilitas asal BBM dalam rantai distribusi. |
| Node Tujuan | `node_tujuan` | String | - | Fasilitas atau wilayah yang menerima BBM. |
| Jenis Infrastruktur | `jenis_infrastruktur` | String | - | Jenis infrastruktur yang menghubungkan node, misalnya submarine pipeline atau distribusi dari fuel terminal. |
| Jenis Pasokan | `jenis_pasokan` | String | - | Asal pasokan berdasarkan sumbernya, seperti kilang atau fuel terminal. |
| Wilayah Distribusi | `wilayah_distribusi` | String | - | Wilayah yang disebut sebagai tujuan distribusi dari sistem pasokan. |
| Rencana Infrastruktur | `rencana_infrastruktur` | String | - | Infrastruktur yang direncanakan untuk memperkuat jaringan distribusi. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class IntegrasiRdmpBalikpapanDenganFuelTerminalTanjungBatuRecord(BaseModel):
    node_asal: str | None = Field(default=None, alias="Node Asal", description="Fasilitas asal BBM dalam rantai distribusi.")
    node_tujuan: str | None = Field(default=None, alias="Node Tujuan", description="Fasilitas atau wilayah yang menerima BBM.")
    jenis_infrastruktur: str | None = Field(default=None, alias="Jenis Infrastruktur", description="Jenis infrastruktur yang menghubungkan node, misalnya submarine pipeline atau distribusi dari fuel terminal.")
    jenis_pasokan: str | None = Field(default=None, alias="Jenis Pasokan", description="Asal pasokan berdasarkan sumbernya, seperti kilang atau fuel terminal.")
    wilayah_distribusi: str | None = Field(default=None, alias="Wilayah Distribusi", description="Wilayah yang disebut sebagai tujuan distribusi dari sistem pasokan.")
    rencana_infrastruktur: str | None = Field(default=None, alias="Rencana Infrastruktur", description="Infrastruktur yang direncanakan untuk memperkuat jaringan distribusi.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
