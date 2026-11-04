# Data Dictionary: Natural Gas and Products

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Natural Gas and Products`
- Publisher: esdm
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [ESDM_ES Natural Gas and Product](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Neraca%20dan%20Ketersediaan%20Energi.xlsx?d=wd12b6b06696f4510aefe45f87a69cd70&csf=1&web=1&e=w4erwj&nav=MTVfezZGQzEyMkZFLTI1RDAtNDFDRS1BOEFELUM3MDlENjJBOTM0QX0)
- Target module: `ingestion/usecases/ketahanan_energi/esdm/natural_gas_and_products/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| tahun | `tahun` | Integer | - | Tahun data |
| kategori | `kategori` | Categorical | - | Produksi, Ekspor, atau Pemanfaatan (pemanfaatan gas per sektor, Gambar 6) |
| indikator | `indikator` | Text | - | Nama indikator, mis. produksi gas, ekspor gas pipa, produksi LNG domestik, ekspor LNG, atau sektor pemanfaatan |
| nilai | `nilai` | Numeric (Decimal) | Tergantung kolom | Nilai indikator. Kosong untuk sektor pemanfaatan yang hanya punya persentase |
| satuan | `satuan` | Categorical | - | MMSCFD, TBTU |
| pangsa_persen | `pangsa_persen` | Numeric (Decimal) | % | Porsi sektor terhadap total pemanfaatan gas (diagram donat) |
| pertumbuhan_yoy_persen | `pertumbuhan_yoy_persen` | Numeric (Decimal) | % | Pertumbuhan dibanding tahun sebelumnya, dari teks |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class NaturalGasAndProductsRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Produksi, Ekspor, atau Pemanfaatan (pemanfaatan gas per sektor, Gambar 6)")
    indikator: str | None = Field(default=None, alias="indikator", description="Nama indikator, mis. produksi gas, ekspor gas pipa, produksi LNG domestik, ekspor LNG, atau sektor pemanfaatan")
    nilai: str | None = Field(default=None, alias="nilai", description="Nilai indikator. Kosong untuk sektor pemanfaatan yang hanya punya persentase")
    satuan: str | None = Field(default=None, alias="satuan", description="MMSCFD, TBTU")
    pangsa_persen: str | None = Field(default=None, alias="pangsa_persen", description="Porsi sektor terhadap total pemanfaatan gas (diagram donat)")
    pertumbuhan_yoy_persen: str | None = Field(default=None, alias="pertumbuhan_yoy_persen", description="Pertumbuhan dibanding tahun sebelumnya, dari teks")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
