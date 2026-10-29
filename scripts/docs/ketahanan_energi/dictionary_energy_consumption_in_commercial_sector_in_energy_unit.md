# Data Dictionary: 5.3.2 Energy Consumption in Commercial Sector in Energy Unit

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `5.3.2 Energy Consumption in Commercial Sector in Energy Unit`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Energy Consumption in Commercial Sector in Energy Unit](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=PQ93o4&nav=MTVfezZCRUNCRUEwLUM2QjgtNDRDMS1BQjlDLTI5RTNEMERDOUY5RX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/energy_consumption_in_commercial_sector_in_energy_unit/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| kategori | `kategori` | Categorical | - | Jenis energi yang dikonsumsi sektor komersial, mis. Traditional Biomass, Solar Water Heater, Total |
| nilai | `nilai` | Numeric (Decimal) | Thousand BOE | Konsumsi energi per kategori dan tahun |
| satuan | `satuan` | Categorical | - | Thousand BOE |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class EnergyConsumptionInCommercialSectorInEnergyUnitRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Jenis energi yang dikonsumsi sektor komersial, mis. Traditional Biomass, Solar Water Heater, Total")
    nilai: str | None = Field(default=None, alias="nilai", description="Konsumsi energi per kategori dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="Thousand BOE")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
