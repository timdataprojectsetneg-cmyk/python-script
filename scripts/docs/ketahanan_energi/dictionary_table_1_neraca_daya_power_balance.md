# Data Dictionary: Table 1 : Neraca Daya / Power Balance

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Table 1 : Neraca Daya / Power Balance`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Daya Mampu vs Beban Puncak](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=d9b09E&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wNDAwLTAwMDAwMDAwMDAwMH0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/table_1_neraca_daya_power_balance/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| unit_pln | `unit_pln` | string | - | Nama unit PLN (UID, UIW, UIP3B, UIK, PLN Indonesia Power, PLN Nusantara Power, dll.), baris agregat "Luar Jawa" dan "Jawa", "Proyek Pembangkitan", atau "Indonesia" |
| tipe_baris | `tipe_baris` | string | - | Jenis baris: "unit", "sub_unit" (provinsi di bawah unit induk, bertanda "-" di sumber), "subtotal_wilayah" (Luar Jawa atau Jawa), "proyek", atau "total" |
| induk_unit | `induk_unit` | string | - | Nama unit induk untuk baris "sub_unit" (misalnya "UID Riau dan Kepulauan Riau" untuk Riau). Bernilai null untuk baris lain |
| kelompok_wilayah | `kelompok_wilayah` | string | - | Kelompok wilayah baris tersebut: "Luar Jawa" atau "Jawa". Bernilai null untuk baris proyek dan total |
| tahun | `tahun` | integer | Tahun | Tahun data (2025) |
| kapasitas_terpasang_mw | `kapasitas_terpasang_mw` | number | MW | Kapasitas terpasang pembangkit milik PLN, sewa, dan IPP. Bernilai null jika di tabel tertulis "-" |
| daya_mampu_mw | `daya_mampu_mw` | number | MW | Daya mampu pembangkit milik PLN, sewa, dan IPP. Bernilai null jika di tabel tertulis "-" |
| beban_puncak_mw | `beban_puncak_mw` | number | MW | Beban puncak. Bernilai null jika di tabel tertulis "-" |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class Table1NeracaDayaPowerBalanceRecord(BaseModel):
    unit_pln: str | None = Field(default=None, alias="unit_pln", description="Nama unit PLN (UID, UIW, UIP3B, UIK, PLN Indonesia Power, PLN Nusantara Power, dll.), baris agregat \"Luar Jawa\" dan \"Jawa\", \"Proyek Pembangkitan\", atau \"Indonesia\"")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"unit\", \"sub_unit\" (provinsi di bawah unit induk, bertanda \"-\" di sumber), \"subtotal_wilayah\" (Luar Jawa atau Jawa), \"proyek\", atau \"total\"")
    induk_unit: str | None = Field(default=None, alias="induk_unit", description="Nama unit induk untuk baris \"sub_unit\" (misalnya \"UID Riau dan Kepulauan Riau\" untuk Riau). Bernilai null untuk baris lain")
    kelompok_wilayah: str | None = Field(default=None, alias="kelompok_wilayah", description="Kelompok wilayah baris tersebut: \"Luar Jawa\" atau \"Jawa\". Bernilai null untuk baris proyek dan total")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2025)")
    kapasitas_terpasang_mw: float | None = Field(default=None, alias="kapasitas_terpasang_mw", description="Kapasitas terpasang pembangkit milik PLN, sewa, dan IPP. Bernilai null jika di tabel tertulis \"-\"")
    daya_mampu_mw: float | None = Field(default=None, alias="daya_mampu_mw", description="Daya mampu pembangkit milik PLN, sewa, dan IPP. Bernilai null jika di tabel tertulis \"-\"")
    beban_puncak_mw: float | None = Field(default=None, alias="beban_puncak_mw", description="Beban puncak. Bernilai null jika di tabel tertulis \"-\"")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
