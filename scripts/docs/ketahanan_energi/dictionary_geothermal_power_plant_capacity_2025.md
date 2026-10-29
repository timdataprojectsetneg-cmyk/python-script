# Data Dictionary: 6.5.2 Geothermal Power Plant Capacity 2025

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `6.5.2 Geothermal Power Plant Capacity 2025`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Geothermal Power Plant Capacity](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=oxlPef&nav=MTVfezNBQzk4ODhFLTlGQzItNENGQS1BNUYxLURCNjg1RDU3QkFDN30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/geothermal_power_plant_capacity_2025/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| kategori | `kategori` | Categorical | - | Tidak terisi pada sumber (selalu `null`) |
| jenis_pembangkit | `jenis_pembangkit` | Categorical | - | Nama PLTP (mis. PLTP Sibayak, PLTP Salak), atau `Total` untuk jumlah keseluruhan |
| nilai | `nilai` | Numeric (Decimal) | MW | Kapasitas terpasang PLTP |
| satuan | `satuan` | Categorical | - | MW |
| provinsi | `provinsi` | Categorical | - | Provinsi lokasi PLTP (`null` untuk baris Total) |
| kode_provinsi | `kode_provinsi` | Integer | - | Kode provinsi (`null` untuk baris Total) |
| ipb_owner | `ipb_owner` | Categorical | - | Pemilik IPB (Izin Panas Bumi) atau pengembang PLTP (`null` untuk baris Total) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class GeothermalPowerPlantCapacity2025Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Tidak terisi pada sumber (selalu null)")
    jenis_pembangkit: str | None = Field(default=None, alias="jenis_pembangkit", description="Nama PLTP, atau Total untuk jumlah keseluruhan")
    nilai: str | None = Field(default=None, alias="nilai", description="Kapasitas terpasang PLTP")
    satuan: str | None = Field(default=None, alias="satuan", description="MW")
    provinsi: str | None = Field(default=None, alias="provinsi", description="Provinsi lokasi PLTP")
    kode_provinsi: int | None = Field(default=None, alias="kode_provinsi", description="Kode provinsi")
    ipb_owner: str | None = Field(default=None, alias="ipb_owner", description="Pemilik IPB atau pengembang PLTP")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
