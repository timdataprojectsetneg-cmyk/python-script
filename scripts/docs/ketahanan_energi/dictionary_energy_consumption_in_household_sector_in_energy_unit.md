# Data Dictionary: 5.2.2 Energy Consumption in Household Sector in Energy Unit

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `5.2.2 Energy Consumption in Household Sector in Energy Unit`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Energy Consumption in Household Sector in Energy Unit](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=XESLsF&nav=MTVfezdGRkNCQzk2LTU1NDQtNEUzNy1BQzcyLUNENjFEMjNCRjU1Qn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/energy_consumption_in_household_sector_in_energy_unit/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Year | `year` | Date | Tahun | Tahun pengamatan konsumsi energi, yaitu 2015–2025. |
| Traditional Biomass | `traditional_biomass` | Numeric (Float) | Thousand BOE | Konsumsi energi yang berasal dari biomassa tradisional pada tahun tertentu. |
| Gas | `gas` | Numeric (Float) | Thousand BOE | Konsumsi energi yang berasal dari gas pada tahun tertentu. |
| Kerosene | `kerosene` | Numeric (Float) | Thousand BOE | Konsumsi energi yang berasal dari minyak tanah pada tahun tertentu. |
| LPG | `lpg` | Numeric (Float) | Thousand BOE | Konsumsi energi yang berasal dari LPG pada tahun tertentu. |
| Biogas | `biogas` | Numeric (Float) | Thousand BOE | Konsumsi energi yang berasal dari biogas pada tahun tertentu. |
| Electricity | `electricity` | Numeric (Float) | Thousand BOE | Konsumsi energi listrik pada tahun tertentu. |
| Total | `total` | Numeric (Float) | Thousand BOE | Total konsumsi energi dari seluruh jenis energi yang tercantum pada tahun tertentu. |

## Generated Pydantic model

```python
from datetime import date as DateType
from pydantic import BaseModel, Field


class EnergyConsumptionInHouseholdSectorInEnergyUnitRecord(BaseModel):
    year: DateType | None = Field(default=None, alias="Year", description="Tahun pengamatan konsumsi energi, yaitu 2015–2025.")
    traditional_biomass: str | None = Field(default=None, alias="Traditional Biomass", description="Konsumsi energi yang berasal dari biomassa tradisional pada tahun tertentu.")
    gas: str | None = Field(default=None, alias="Gas", description="Konsumsi energi yang berasal dari gas pada tahun tertentu.")
    kerosene: str | None = Field(default=None, alias="Kerosene", description="Konsumsi energi yang berasal dari minyak tanah pada tahun tertentu.")
    lpg: str | None = Field(default=None, alias="LPG", description="Konsumsi energi yang berasal dari LPG pada tahun tertentu.")
    biogas: str | None = Field(default=None, alias="Biogas", description="Konsumsi energi yang berasal dari biogas pada tahun tertentu.")
    electricity: str | None = Field(default=None, alias="Electricity", description="Konsumsi energi listrik pada tahun tertentu.")
    total: str | None = Field(default=None, alias="Total", description="Total konsumsi energi dari seluruh jenis energi yang tercantum pada tahun tertentu.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
