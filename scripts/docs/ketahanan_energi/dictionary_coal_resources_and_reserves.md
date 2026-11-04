# Data Dictionary: 6.1.1 Coal Resources and Reserves

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `6.1.1 Coal Resources and Reserves`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Coal Resources and Reserve](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=W5TF09&nav=MTVfe0ZGMEQ2RTBDLUM2NjAtNDU5MC04M0FELTAyRjQ5RTdCNDlGRn0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/coal_resources_and_reserves/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Province Code | `province_code` | Integer | - | Kode provinsi sesuai kode Kementerian Dalam Negeri |
| Province | `province` | String | - | Nama provinsi; baris TOTAL untuk agregat nasional |
| Exploration Target | `exploration_target` | Numeric (Float) | Juta ton | Target eksplorasi batubara pada provinsi bersangkutan |
| Total Inventory | `total_inventory` | Numeric (Float) | Juta ton | Total inventori batubara pada provinsi bersangkutan |
| Resources - Inferred | `resources_inferred` | Numeric (Float) | Juta ton | Sumber daya batubara kelas tereka (inferred) |
| Resources - Indicated | `resources_indicated` | Numeric (Float) | Juta ton | Sumber daya batubara kelas terunjuk (indicated) |
| Resources - Measured | `resources_measured` | Numeric (Float) | Juta ton | Sumber daya batubara kelas terukur (measured) |
| Resources - Total | `resources_total` | Numeric (Float) | Juta ton | Total sumber daya batubara (inferred + indicated + measured) |
| Reserves | `reserves` | Numeric (Float) | Juta ton | Cadangan batubara pada provinsi bersangkutan |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class CoalResourcesAndReservesRecord(BaseModel):
    province_code: int | None = Field(default=None, alias="Province Code", description="Kode provinsi sesuai kode Kementerian Dalam Negeri")
    province: str | None = Field(default=None, alias="Province", description="Nama provinsi; baris TOTAL untuk agregat nasional")
    exploration_target: str | None = Field(default=None, alias="Exploration Target", description="Target eksplorasi batubara pada provinsi bersangkutan")
    total_inventory: str | None = Field(default=None, alias="Total Inventory", description="Total inventori batubara pada provinsi bersangkutan")
    resources_inferred: str | None = Field(default=None, alias="Resources - Inferred", description="Sumber daya batubara kelas tereka (inferred)")
    resources_indicated: str | None = Field(default=None, alias="Resources - Indicated", description="Sumber daya batubara kelas terunjuk (indicated)")
    resources_measured: str | None = Field(default=None, alias="Resources - Measured", description="Sumber daya batubara kelas terukur (measured)")
    resources_total: str | None = Field(default=None, alias="Resources - Total", description="Total sumber daya batubara (inferred + indicated + measured)")
    reserves: str | None = Field(default=None, alias="Reserves", description="Cadangan batubara pada provinsi bersangkutan")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
