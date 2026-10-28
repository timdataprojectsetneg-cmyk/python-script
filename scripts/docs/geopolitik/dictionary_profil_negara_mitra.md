# Data Dictionary: Profil Negara Mitra

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Profil Negara Mitra`
- Publisher: World Bank
- Data access: `api`
- Update frequency: Sesuai revisi metadata negara
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Hubungan Bilateral (1).xlsx
- Target module: `ingestion/usecases/geopolitik/world_bank/profil_negara_mitra/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| id | `id` | String | ISO3 | Kode ekonomi/negara World Bank. |
| name | `name` | String | - | Nama negara/ekonomi sumber. |
| capitalCity | `capitalcity` | String | - | Nama ibu kota menurut metadata sumber. |
| region | `region` | String | - | Kelompok kawasan World Bank. |
| incomeLevel | `incomelevel` | String | - | Kelompok pendapatan World Bank. |
| latitude | `latitude` | Decimal | Derajat | Lintang ibu kota. |
| longitude | `longitude` | Decimal | Derajat | Bujur ibu kota. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class ProfilNegaraMitraRecord(BaseModel):
    id: str | None = Field(default=None, alias="id", description="Kode ekonomi/negara World Bank.")
    name: str | None = Field(default=None, alias="name", description="Nama negara/ekonomi sumber.")
    capitalcity: str | None = Field(default=None, alias="capitalCity", description="Nama ibu kota menurut metadata sumber.")
    region: str | None = Field(default=None, alias="region", description="Kelompok kawasan World Bank.")
    incomelevel: str | None = Field(default=None, alias="incomeLevel", description="Kelompok pendapatan World Bank.")
    latitude: float | None = Field(default=None, alias="latitude", description="Lintang ibu kota.")
    longitude: float | None = Field(default=None, alias="longitude", description="Bujur ibu kota.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
