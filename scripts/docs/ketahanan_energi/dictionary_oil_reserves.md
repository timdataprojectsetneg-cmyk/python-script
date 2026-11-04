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
| tahun (number), kategori (string), wilayah (string), nilai (number), satuan (string) | `tahun_number_kategori_string_wilayah_string_nilai_number_satuan_string` | number | - | Tahun cadangan pada wilayah |
| kategori | `kategori` | string | - | Cadangan  (P1 + P2 + P3) |
| wilayah | `wilayah` | string | - | Wilayah cadangan minyak bumi; pembagian wilayah tidak berdasarkan batas administratif. Baris Total untuk agregat nasional |
| nilai | `nilai` | Numeric (Float) | MMSTB | nilai cadangan pada wilayah |
| satuan | `satuan` | string | - | Total cadangan pada wilayah bersangkutan (P1 + P2 + P3) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class OilReservesRecord(BaseModel):
    tahun_number_kategori_string_wilayah_string_nilai_number_satuan_string: float | None = Field(default=None, alias="tahun (number), kategori (string), wilayah (string), nilai (number), satuan (string)", description="Tahun cadangan pada wilayah")
    kategori: str | None = Field(default=None, alias="kategori", description="Cadangan  (P1 + P2 + P3)")
    wilayah: str | None = Field(default=None, alias="wilayah", description="Wilayah cadangan minyak bumi; pembagian wilayah tidak berdasarkan batas administratif. Baris Total untuk agregat nasional")
    nilai: str | None = Field(default=None, alias="nilai", description="nilai cadangan pada wilayah")
    satuan: str | None = Field(default=None, alias="satuan", description="Total cadangan pada wilayah bersangkutan (P1 + P2 + P3)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
