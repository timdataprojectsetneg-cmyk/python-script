# Data Dictionary: Final Energy Consumption

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Final Energy Consumption`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_ES Final Energy Consumption](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=ETJpiJ&nav=MTVfezM5QjE3NUE5LUYzRjktNDVCMi05NEMyLTMyRDREMzU4RDBGQ30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/final_energy_consumption/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Year | `year` | Integer | Tahun | Tahun/periode data pada tabel konsumsi energi final per jenis energi (2015-2025). |
| Traditional Biomass | `traditional_biomass` | Numeric | Thousand BOE | Konsumsi energi dari biomassa tradisional. |
| Industrial Biomass | `industrial_biomass` | Numeric | Thousand BOE | Konsumsi energi dari biomassa industri. |
| Solar Water Heater | `solar_water_heater` | Numeric | Thousand BOE | Konsumsi energi dari pemanas air tenaga surya. Bernilai "n.a" pada 2015-2021. |
| Direct Use of Geothermal | `direct_use_of_geothermal` | Numeric | Thousand BOE | Konsumsi energi dari pemanfaatan langsung panas bumi. Bernilai "n.a" pada 2015-2021. |
| Coal | `coal` | Numeric | Thousand BOE | Konsumsi energi dari batu bara. Memiliki catatan 1). |
| Natural Gas | `natural_gas` | Numeric | Thousand BOE | Konsumsi energi dari gas alam. |
| Oil Fuel | `oil_fuel` | Numeric | Thousand BOE | Konsumsi energi dari bahan bakar minya |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class FinalEnergyConsumptionRecord(BaseModel):
    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data pada tabel konsumsi energi final per jenis energi (2015-2025).")
    traditional_biomass: str | None = Field(default=None, alias="Traditional Biomass", description="Konsumsi energi dari biomassa tradisional.")
    industrial_biomass: str | None = Field(default=None, alias="Industrial Biomass", description="Konsumsi energi dari biomassa industri.")
    solar_water_heater: str | None = Field(default=None, alias="Solar Water Heater", description="Konsumsi energi dari pemanas air tenaga surya. Bernilai \"n.a\" pada 2015-2021.")
    direct_use_of_geothermal: str | None = Field(default=None, alias="Direct Use of Geothermal", description="Konsumsi energi dari pemanfaatan langsung panas bumi. Bernilai \"n.a\" pada 2015-2021.")
    coal: str | None = Field(default=None, alias="Coal", description="Konsumsi energi dari batu bara. Memiliki catatan 1).")
    natural_gas: str | None = Field(default=None, alias="Natural Gas", description="Konsumsi energi dari gas alam.")
    oil_fuel: str | None = Field(default=None, alias="Oil Fuel", description="Konsumsi energi dari bahan bakar minya")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
