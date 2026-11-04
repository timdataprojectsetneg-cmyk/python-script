# Data Dictionary: 5.1.2 Energy Consumption in Industrial Sector in Energy Unit

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `5.1.2 Energy Consumption in Industrial Sector in Energy Unit`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Energy Consumption in Industrial Sector in Energy Unit](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=18TJLT&nav=MTVfezIxQzkyRTlDLUI0MkMtNDMxNi05MkQwLTFEMTdDMkRFNDRDRX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/energy_consumption_in_industrial_sector_in_energy_unit/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Year | `year` | Date | Tahun | Tahun pengamatan konsumsi energi, yaitu 2015–2025. |
| Industrial Biomass | `industrial_biomass` | Numeric (Float) | Thousand BOE | Konsumsi energi yang berasal dari biomassa industri pada tahun tertentu. |
| Direct Use Geothermal | `direct_use_geothermal` | Numeric (Float) | Thousand BOE | Konsumsi energi panas bumi yang digunakan secara langsung pada tahun tertentu. |
| Coal | `coal` | Numeric (Float) | Thousand BOE | Konsumsi energi yang berasal dari batu bara pada tahun tertentu. |
| Briquette | `briquette` | Numeric (Float) | Thousand BOE | Konsumsi energi yang berasal dari briket pada tahun tertentu. |
| Gas | `gas` | Numeric (Float) | Thousand BOE | Konsumsi energi yang berasal dari gas pada tahun tertentu. |
| Kerosene | `kerosene` | Numeric (Float) | Thousand BOE | Konsumsi energi yang berasal dari minyak tanah pada tahun tertentu. |
| Gasoline RON 90 | `gasoline_ron_90` | Numeric (Float) | Thousand BOE | Konsumsi bensin RON 90 pada tahun tertentu. |
| Gasoline RON 92 | `gasoline_ron_92` | Numeric (Float) | Thousand BOE | Konsumsi bensin RON 92 pada tahun tertentu. |
| Gasoline RON 95+98+100 | `gasoline_ron_95_98_100` | Numeric (Float) | Thousand BOE | Konsumsi bensin dengan RON 95, 98, dan 100 pada tahun tertentu. |
| Gasoil CN 48 | `gasoil_cn_48` | Numeric (Float) | Thousand BOE | Konsumsi gasoil dengan CN 48 pada tahun tertentu. |
| Bio Gasoil | `bio_gasoil` | Numeric (Float) | Thousand BOE | Konsumsi bio-gasoil pada tahun tertentu. |
| Gasoil CN 51 | `gasoil_cn_51` | Numeric (Float) | Thousand BOE | Konsumsi gasoil dengan CN 51 pada tahun tertentu. |
| Gasoil CN 53 | `gasoil_cn_53` | Numeric (Float) | Thousand BOE | Konsumsi gasoil dengan CN 53 pada tahun tertentu. |
| MDF | `mdf` | Numeric (Float) | Thousand BOE | Konsumsi MDF pada tahun tertentu. |
| Fuel Oil | `fuel_oil` | Numeric (Float) | Thousand BOE | Konsumsi fuel oil pada tahun tertentu. |
| LPG | `lpg` | Numeric (Float) | Thousand BOE | Konsumsi LPG pada tahun tertentu. |
| Electricity | `electricity` | Numeric (Float) | Thousand BOE | Konsumsi energi listrik pada tahun tertentu. |
| Total Oil Fuel | `total_oil_fuel` | Numeric (Float) | Thousand BOE | Total konsumsi kelompok oil fuel pada tahun tertentu. |
| Total | `total` | Numeric (Float) | Thousand BOE | Total konsumsi energi pada tahun tertentu. |

## Generated Pydantic model

```python
from datetime import date as DateType
from pydantic import BaseModel, Field


class EnergyConsumptionInIndustrialSectorInEnergyUnitRecord(BaseModel):
    year: DateType | None = Field(default=None, alias="Year", description="Tahun pengamatan konsumsi energi, yaitu 2015–2025.")
    industrial_biomass: str | None = Field(default=None, alias="Industrial Biomass", description="Konsumsi energi yang berasal dari biomassa industri pada tahun tertentu.")
    direct_use_geothermal: str | None = Field(default=None, alias="Direct Use Geothermal", description="Konsumsi energi panas bumi yang digunakan secara langsung pada tahun tertentu.")
    coal: str | None = Field(default=None, alias="Coal", description="Konsumsi energi yang berasal dari batu bara pada tahun tertentu.")
    briquette: str | None = Field(default=None, alias="Briquette", description="Konsumsi energi yang berasal dari briket pada tahun tertentu.")
    gas: str | None = Field(default=None, alias="Gas", description="Konsumsi energi yang berasal dari gas pada tahun tertentu.")
    kerosene: str | None = Field(default=None, alias="Kerosene", description="Konsumsi energi yang berasal dari minyak tanah pada tahun tertentu.")
    gasoline_ron_90: str | None = Field(default=None, alias="Gasoline RON 90", description="Konsumsi bensin RON 90 pada tahun tertentu.")
    gasoline_ron_92: str | None = Field(default=None, alias="Gasoline RON 92", description="Konsumsi bensin RON 92 pada tahun tertentu.")
    gasoline_ron_95_98_100: str | None = Field(default=None, alias="Gasoline RON 95+98+100", description="Konsumsi bensin dengan RON 95, 98, dan 100 pada tahun tertentu.")
    gasoil_cn_48: str | None = Field(default=None, alias="Gasoil CN 48", description="Konsumsi gasoil dengan CN 48 pada tahun tertentu.")
    bio_gasoil: str | None = Field(default=None, alias="Bio Gasoil", description="Konsumsi bio-gasoil pada tahun tertentu.")
    gasoil_cn_51: str | None = Field(default=None, alias="Gasoil CN 51", description="Konsumsi gasoil dengan CN 51 pada tahun tertentu.")
    gasoil_cn_53: str | None = Field(default=None, alias="Gasoil CN 53", description="Konsumsi gasoil dengan CN 53 pada tahun tertentu.")
    mdf: str | None = Field(default=None, alias="MDF", description="Konsumsi MDF pada tahun tertentu.")
    fuel_oil: str | None = Field(default=None, alias="Fuel Oil", description="Konsumsi fuel oil pada tahun tertentu.")
    lpg: str | None = Field(default=None, alias="LPG", description="Konsumsi LPG pada tahun tertentu.")
    electricity: str | None = Field(default=None, alias="Electricity", description="Konsumsi energi listrik pada tahun tertentu.")
    total_oil_fuel: str | None = Field(default=None, alias="Total Oil Fuel", description="Total konsumsi kelompok oil fuel pada tahun tertentu.")
    total: str | None = Field(default=None, alias="Total", description="Total konsumsi energi pada tahun tertentu.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
