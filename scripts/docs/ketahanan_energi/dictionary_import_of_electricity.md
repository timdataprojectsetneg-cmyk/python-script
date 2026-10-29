# Data Dictionary: 6.4.3 Import of Electricity

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `6.4.3 Import of Electricity`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Import of Electricity](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=J7Jbg2&nav=MTVfezVGNEQ5ODI3LTZFNkEtNDQ5MC1BMDBELUNEQjRDQTg2M0Y1N30)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/import_of_electricity/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| kategori | `kategori` | Categorical | - | Jenis pembangkit sumber listrik impor, mis. Hydro PP |
| nilai | `nilai` | Numeric (Decimal) | GWh | Energi listrik impor per kategori dan tahun |
| satuan | `satuan` | Categorical | - | GWh |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class ImportOfElectricityRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Jenis pembangkit sumber listrik impor, mis. Hydro PP")
    nilai: str | None = Field(default=None, alias="nilai", description="Energi listrik impor per kategori dan tahun")
    satuan: str | None = Field(default=None, alias="satuan", description="GWh")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
