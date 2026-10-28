# Data Dictionary: 6.2.1 Oil Reserves

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `6.2.1 Oil Reserves`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_Oil Reserves](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=Akbvsw&nav=MTVfezZCN0JERjkzLTJGMUItNDRENi05NDk4LTgyNTE2REY5RUU3OX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/oil_reserves/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| kategori | `kategori` | Categorical | - | Kapasitas Terpasang (Gambar 7) atau Produksi Listrik (Gambar 8) |
| jenis_pembangkit | `jenis_pembangkit` | Categorical | - | NRE PP, Steam PP, Gas PP, Combined Cycle PP, Diesel PP, Gas Engine PP, atau Total |
| nilai | `nilai` | Numeric (Decimal) | Tergantung kolom | Kapasitas atau produksi per jenis pembangkit |
| satuan | `satuan` | Categorical | - | GW (kapasitas), TWh (produksi) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class OilReservesRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Kapasitas Terpasang (Gambar 7) atau Produksi Listrik (Gambar 8)")
    jenis_pembangkit: str | None = Field(default=None, alias="jenis_pembangkit", description="NRE PP, Steam PP, Gas PP, Combined Cycle PP, Diesel PP, Gas Engine PP, atau Total")
    nilai: str | None = Field(default=None, alias="nilai", description="Kapasitas atau produksi per jenis pembangkit")
    satuan: str | None = Field(default=None, alias="satuan", description="GW (kapasitas), TWh (produksi)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
