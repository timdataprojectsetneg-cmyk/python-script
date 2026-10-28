# Data Dictionary: Artikel KONTAN - Pertamina Catat 57 Juta NIK Pembeli LPG 3 Kg, Siap Jalankan Subsidi Tepat Sasaran

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Artikel KONTAN - Pertamina Catat 57 Juta NIK Pembeli LPG 3 Kg, Siap Jalankan Subsidi Tepat Sasaran`
- Publisher: pertamina
- Data access: `scraper`
- Update frequency: Insidental
- Eligible: `True`
- Data Dictionary file: [Pertamina PPN - Subsidi Tepat LPG](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=0OvRhy&nav=MTVfezEzMTE0QTk0LThFQzgtNDE2RC1COTczLTMxM0I4RTdCNTlFNH0)
- Target module: `ingestion/usecases/ketahanan_energi/pertamina/pertamina_catat_57_juta_nik_pembeli_lpg_3_kg_siap/models.py`

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


class PertaminaCatat57JutaNikPembeliLpg3KgSiapRecord(BaseModel):
    periode: int | None = Field(default=None, alias="Periode", description="Tahun buku laporan keuangan")
    komponen_biaya: str | None = Field(default=None, alias="Komponen Biaya", description="Pos biaya pada cost of sales PGN")
    jenis_biaya: str | None = Field(default=None, alias="Jenis Biaya", description="Raw material, service, labor, depreciation, maintenance, fuel, overhead")
    nilai: float | None = Field(default=None, alias="Nilai", description="Nilai komponen biaya sesuai laporan keuangan")
    tahun_pembanding: int | None = Field(default=None, alias="Tahun Pembanding", description="Tahun 2024 sebagai comparative figure")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
