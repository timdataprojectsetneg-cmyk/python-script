# Data Dictionary: APBN KiTa Edisi September 2026 - Realisasi Subsidi dan Kompensasi s.d. 31 Agustus 2026

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `APBN KiTa Edisi September 2026 - Realisasi Subsidi dan Kompensasi s.d. 31 Agustus 2026`
- Publisher: kemenkeu
- Data access: `pdf`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Kemenkeu - Realisasi Subsidi dan Kompensasi](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=Fdx1eD&nav=MTVfe0FFQjZBRUE5LUM5NEQtNDE3Ni04RkMwLUE2ODUxN0FBNjVDMn0)
- Target module: `ingestion/usecases/ketahanan_energi/kemenkeu/realisasi_subsidi_dan_kompensasi_s_d_31_agustus_2026/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Periode | `periode` | Integer | Tahun | Tahun buku laporan keuangan |
| Komponen Biaya | `komponen_biaya` | String | - | Pos biaya pada cost of sales PGN |
| Jenis Biaya | `jenis_biaya` | Categorical | - | Raw material, service, labor, depreciation, maintenance, fuel, overhead |
| Nilai | `nilai` | Decimal | USD | Nilai komponen biaya sesuai laporan keuangan |
| Tahun Pembanding | `tahun_pembanding` | Integer | Tahun | Tahun 2024 sebagai comparative figure |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class RealisasiSubsidiDanKompensasiSD31Agustus2026Record(BaseModel):
    periode: int | None = Field(default=None, alias="Periode", description="Tahun buku laporan keuangan")
    komponen_biaya: str | None = Field(default=None, alias="Komponen Biaya", description="Pos biaya pada cost of sales PGN")
    jenis_biaya: str | None = Field(default=None, alias="Jenis Biaya", description="Raw material, service, labor, depreciation, maintenance, fuel, overhead")
    nilai: float | None = Field(default=None, alias="Nilai", description="Nilai komponen biaya sesuai laporan keuangan")
    tahun_pembanding: int | None = Field(default=None, alias="Tahun Pembanding", description="Tahun 2024 sebagai comparative figure")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
