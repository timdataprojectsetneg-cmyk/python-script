# Data Dictionary: 6.2.6 Import of Refined Products

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `6.2.6 Import of Refined Products`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Import of Redifined Product](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=hktXEB&nav=MTVfezVFMjAzNUE2LTIwRDAtNDQ1Ri04NDkyLUNDMDg5MEQzQkIxNH0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/import_of_refined_products/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Year | `year` | Integer | Tahun | Tahun/periode data |
| Avtur | `avtur` | Numeric | Thousand KL | Volume impor Avtur per tahun |
| Avgas | `avgas` | Numeric | Thousand KL | Volume impor Avgas per tahun |
| Gasoline RON 88 & 90 | `gasoline_ron_88_90` | Numeric | Thousand KL | Volume impor Bensin RON 88 & 90 per tahun |
| Gasoline RON 95 | `gasoline_ron_95` | Numeric | Thousand KL | Volume impor Bensin RON 95 per tahun |
| Gasoline RON 92 | `gasoline_ron_92` | Numeric | Thousand KL | Volume impor Bensin RON 92 per tahun |
| Naphtha | `naphtha` | Numeric | Thousand KL | Volume impor Naphtha per tahun |
| HOMC | `homc` | Numeric | Thousand KL | Volume impor HOMC per tahun |
| Gasoil | `gasoil` | Numeric | Thousand KL | Volume impor Gasoil per tahun |
| Fuel Oil | `fuel_oil` | Numeric | Thousand KL | Volume impor Fuel Oil per tahun |
| MDF | `mdf` | Numeric | Thousand KL | Volume impor MDF per tahun |
| Total Oil Fuel | `total_oil_fuel` | Numeric | Thousand KL | Total impor seluruh jenis BBM per tahun |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class ImportOfRefinedProductsRecord(BaseModel):
    year: int | None = Field(default=None, alias="Year", description="Tahun/periode data")
    avtur: str | None = Field(default=None, alias="Avtur", description="Volume impor Avtur per tahun")
    avgas: str | None = Field(default=None, alias="Avgas", description="Volume impor Avgas per tahun")
    gasoline_ron_88_90: str | None = Field(default=None, alias="Gasoline RON 88 & 90", description="Volume impor Bensin RON 88 & 90 per tahun")
    gasoline_ron_95: str | None = Field(default=None, alias="Gasoline RON 95", description="Volume impor Bensin RON 95 per tahun")
    gasoline_ron_92: str | None = Field(default=None, alias="Gasoline RON 92", description="Volume impor Bensin RON 92 per tahun")
    naphtha: str | None = Field(default=None, alias="Naphtha", description="Volume impor Naphtha per tahun")
    homc: str | None = Field(default=None, alias="HOMC", description="Volume impor HOMC per tahun")
    gasoil: str | None = Field(default=None, alias="Gasoil", description="Volume impor Gasoil per tahun")
    fuel_oil: str | None = Field(default=None, alias="Fuel Oil", description="Volume impor Fuel Oil per tahun")
    mdf: str | None = Field(default=None, alias="MDF", description="Volume impor MDF per tahun")
    total_oil_fuel: str | None = Field(default=None, alias="Total Oil Fuel", description="Total impor seluruh jenis BBM per tahun")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
