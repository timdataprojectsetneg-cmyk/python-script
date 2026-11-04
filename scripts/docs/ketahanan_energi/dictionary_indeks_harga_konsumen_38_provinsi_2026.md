# Data Dictionary: BPS - Indeks Harga Konsumen 38 Provinsi (2022=100), 2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `BPS - Indeks Harga Konsumen 38 Provinsi (2022=100), 2026`
- Publisher: bps
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [BPS - IHK 38 Provinsi 2026](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=JdAJHl&nav=MTVfe0MyQzVDRDFFLTMxMEMtNEE0RS04RDRELTA0NzQxRUVEMUUxM30)
- Target module: `ingestion/usecases/ketahanan_energi/bps/indeks_harga_konsumen_38_provinsi_2026/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Provinsi | `provinsi` | String/Kategorikal | Provinsi | Nama provinsi tempat indeks harga konsumen diukur |
| Tahun | `tahun` | Integer | Tahun | Tahun observasi IHK |
| Bulan | `bulan` | String/Kategorikal | Bulan | Bulan observasi IHK |
| IHK | `ihk` | Numerik/Decimal | Indeks | Indeks Harga Konsumen dengan tahun dasar 2022 = 100 yang menggambarkan tingkat harga konsumen pada provinsi dan periode tertentu |
| Tahun Dasar | `tahun_dasar` | Integer | Tahun | Tahun dasar yang digunakan dalam perhitungan indeks, yaitu 2022 |
| Periode Observasi | `periode_observasi` | Date/Period | Bulan-Tahun | Periode pengamatan yang menggabungkan tahun dan bulan |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class IndeksHargaKonsumen38Provinsi2026Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi tempat indeks harga konsumen diukur")
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun observasi IHK")
    bulan: str | None = Field(default=None, alias="Bulan", description="Bulan observasi IHK")
    ihk: str | None = Field(default=None, alias="IHK", description="Indeks Harga Konsumen dengan tahun dasar 2022 = 100 yang menggambarkan tingkat harga konsumen pada provinsi dan periode tertentu")
    tahun_dasar: int | None = Field(default=None, alias="Tahun Dasar", description="Tahun dasar yang digunakan dalam perhitungan indeks, yaitu 2022")
    periode_observasi: str | None = Field(default=None, alias="Periode Observasi", description="Periode pengamatan yang menggabungkan tahun dan bulan")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
