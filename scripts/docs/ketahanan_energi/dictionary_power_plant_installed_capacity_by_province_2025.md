# Data Dictionary: 6.4.9 Power Plant Installed Capacity by Province 2025

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `6.4.9 Power Plant Installed Capacity by Province 2025`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Power Plant Installed Capacity by Province 2025](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=WUECDL&nav=MTVfe0E1MjFEN0VDLTAwOEQtNDRFOS1BNjRBLTE1MzQ0NzgyQ0IzRH0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/power_plant_installed_capacity_by_province_2025/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | Tahun | Tahun data kapasitas terpasang pembangkit (2025) |
| provinsi | `provinsi` | String | - | Nama provinsi sesuai tabel sumber (38 provinsi) |
| kategori | `kategori` | String | - | Jenis pembangkit: Hydro PP, Mini Hydro PP, Micro Hydro PP, Geothermal PP, Solar PP, Wind PP, Biogas PP, Biomass PP, Biofuel PP, Waste PP, Diesel PP, Steam PP, Gas PP, Coal Gasification PP, Combined Gas-Steam PP, Gas Engine PP, Other PP, Total (jumlah seluruh jenis pembangkit di provinsi tersebut) |
| nilai | `nilai` | Decimal | MW | Kapasitas terpasang pembangkit listrik (megawatt); tanda "-" pada sumber ditulis 0 |
| satuan | `satuan` | String | - | Satuan nilai, yaitu MW (megawatt) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PowerPlantInstalledCapacityByProvince2025Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data kapasitas terpasang pembangkit (2025)")
    provinsi: str | None = Field(default=None, alias="provinsi", description="Nama provinsi sesuai tabel sumber (38 provinsi)")
    kategori: str | None = Field(default=None, alias="kategori", description="Jenis pembangkit: Hydro PP, Mini Hydro PP, Micro Hydro PP, Geothermal PP, Solar PP, Wind PP, Biogas PP, Biomass PP, Biofuel PP, Waste PP, Diesel PP, Steam PP, Gas PP, Coal Gasification PP, Combined Gas-Steam PP, Gas Engine PP, Other PP, Total (jumlah seluruh jenis pembangkit di provinsi tersebut)")
    nilai: float | None = Field(default=None, alias="nilai", description="Kapasitas terpasang pembangkit listrik (megawatt); tanda \"-\" pada sumber ditulis 0")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai, yaitu MW (megawatt)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
