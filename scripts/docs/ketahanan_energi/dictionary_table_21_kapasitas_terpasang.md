# Data Dictionary: Table 21: Kapasitas Terpasang (MW)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Table 21: Kapasitas Terpasang (MW)`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Jenis Energi Terpasang](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Keandalan%20Penyediaan%20Tenaga%20Listrik.xlsx?d=we036a48c5f804babbfc372b88ffc10e5&csf=1&web=1&e=1WRByC&nav=MTVfezM2NjhGNDgxLURGN0YtNDhCNC1BNjRGLThENENGM0VCRjc4OX0)
- Target module: `ingestion/usecases/ketahanan_energi/pln/table_21_kapasitas_terpasang/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| unit_pln | `unit_pln` | string | - | Nama unit PLN, baris agregat "Luar Jawa" dan "Jawa", "Proyek Pembangkitan", "Indonesia", atau "% terhadap total" |
| tipe_baris | `tipe_baris` | string | - | Jenis baris: "unit", "sub_unit", "subtotal_wilayah", "proyek", "total", atau "persentase" (baris "%" di bawah Indonesia) |
| induk_unit | `induk_unit` | string | - | Nama unit induk untuk baris "sub_unit". Bernilai null untuk baris lain |
| kelompok_wilayah | `kelompok_wilayah` | string | - | Kelompok wilayah: "Luar Jawa" atau "Jawa". Bernilai null untuk baris proyek, total, dan persentase |
| tahun | `tahun` | integer | Tahun | Tahun data (2025) |
| plta_hydro_mw | `plta_hydro_mw` | number | MW | Kapasitas PLTA (Hydro). Null jika "-" |
| pltm_mini_hydro_mw | `pltm_mini_hydro_mw` | number | MW | Kapasitas PLTM (Mini Hydro). Null jika "-" |
| pltmh_micro_hydro_mw | `pltmh_micro_hydro_mw` | number | MW | Kapasitas PLTMH (Micro Hydro). Null jika "-" |
| pltu_steam_mw | `pltu_steam_mw` | number | MW | Kapasitas PLTU (Steam). Null jika "-" |
| pltg_gas_mw | `pltg_gas_mw` | number | MW | Kapasitas PLTG (Gas). Null jika "-" |
| pltgu_combined_cycle_mw | `pltgu_combined_cycle_mw` | number | MW | Kapasitas PLTGU (Combined Cycle). Null jika "-" |
| pltp_geothermal_mw | `pltp_geothermal_mw` | number | MW | Kapasitas PLTP (Geothermal). Null jika "-" |
| pltd_diesel_mw | `pltd_diesel_mw` | number | MW | Kapasitas PLTD (Diesel). Null jika "-" |
| pltmg_gas_engine_mw | `pltmg_gas_engine_mw` | number | MW | Kapasitas PLTMG (Gas Engine). Null jika "-" |
| plt_surya_solar_mw | `plt_surya_solar_mw` | number | MW | Kapasitas PLT Surya (Solar). Null jika "-" |
| plt_bayu_wind_mw | `plt_bayu_wind_mw` | number | MW | Kapasitas PLT Bayu (Wind). Null jika "-" |
| plt_biomassa_mw | `plt_biomassa_mw` | number | MW | Kapasitas PLT Biomassa (Biomass). Null jika "-" |
| sub_jumlah_mw | `sub_jumlah_mw` | number | MW | Sub jumlah kapasitas dari seluruh jenis pembangkit milik PLN. Null jika "-" |
| sub_jumlah_persen | `sub_jumlah_persen` | number | % | Persentase sub jumlah terhadap total Indonesia. Null jika "-" |
| sewa_mw | `sewa_mw` | number | MW | Kapasitas pembangkit sewa (Leased). Null jika "-" |
| ipp_mw | `ipp_mw` | number | MW | Kapasitas pembangkit IPP. Null jika "-" |
| jumlah_mw | `jumlah_mw` | number | MW | Jumlah total kapasitas (sub jumlah + sewa + IPP). Null jika "-" |
| jumlah_persen | `jumlah_persen` | number | % | Persentase jumlah terhadap total Indonesia. Null jika "-" |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class Table21KapasitasTerpasangRecord(BaseModel):
    unit_pln: str | None = Field(default=None, alias="unit_pln", description="Nama unit PLN, baris agregat \"Luar Jawa\" dan \"Jawa\", \"Proyek Pembangkitan\", \"Indonesia\", atau \"% terhadap total\"")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"unit\", \"sub_unit\", \"subtotal_wilayah\", \"proyek\", \"total\", atau \"persentase\" (baris \"%\" di bawah Indonesia)")
    induk_unit: str | None = Field(default=None, alias="induk_unit", description="Nama unit induk untuk baris \"sub_unit\". Bernilai null untuk baris lain")
    kelompok_wilayah: str | None = Field(default=None, alias="kelompok_wilayah", description="Kelompok wilayah: \"Luar Jawa\" atau \"Jawa\". Bernilai null untuk baris proyek, total, dan persentase")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2025)")
    plta_hydro_mw: float | None = Field(default=None, alias="plta_hydro_mw", description="Kapasitas PLTA (Hydro). Null jika \"-\"")
    pltm_mini_hydro_mw: float | None = Field(default=None, alias="pltm_mini_hydro_mw", description="Kapasitas PLTM (Mini Hydro). Null jika \"-\"")
    pltmh_micro_hydro_mw: float | None = Field(default=None, alias="pltmh_micro_hydro_mw", description="Kapasitas PLTMH (Micro Hydro). Null jika \"-\"")
    pltu_steam_mw: float | None = Field(default=None, alias="pltu_steam_mw", description="Kapasitas PLTU (Steam). Null jika \"-\"")
    pltg_gas_mw: float | None = Field(default=None, alias="pltg_gas_mw", description="Kapasitas PLTG (Gas). Null jika \"-\"")
    pltgu_combined_cycle_mw: float | None = Field(default=None, alias="pltgu_combined_cycle_mw", description="Kapasitas PLTGU (Combined Cycle). Null jika \"-\"")
    pltp_geothermal_mw: float | None = Field(default=None, alias="pltp_geothermal_mw", description="Kapasitas PLTP (Geothermal). Null jika \"-\"")
    pltd_diesel_mw: float | None = Field(default=None, alias="pltd_diesel_mw", description="Kapasitas PLTD (Diesel). Null jika \"-\"")
    pltmg_gas_engine_mw: float | None = Field(default=None, alias="pltmg_gas_engine_mw", description="Kapasitas PLTMG (Gas Engine). Null jika \"-\"")
    plt_surya_solar_mw: float | None = Field(default=None, alias="plt_surya_solar_mw", description="Kapasitas PLT Surya (Solar). Null jika \"-\"")
    plt_bayu_wind_mw: float | None = Field(default=None, alias="plt_bayu_wind_mw", description="Kapasitas PLT Bayu (Wind). Null jika \"-\"")
    plt_biomassa_mw: float | None = Field(default=None, alias="plt_biomassa_mw", description="Kapasitas PLT Biomassa (Biomass). Null jika \"-\"")
    sub_jumlah_mw: float | None = Field(default=None, alias="sub_jumlah_mw", description="Sub jumlah kapasitas dari seluruh jenis pembangkit milik PLN. Null jika \"-\"")
    sub_jumlah_persen: float | None = Field(default=None, alias="sub_jumlah_persen", description="Persentase sub jumlah terhadap total Indonesia. Null jika \"-\"")
    sewa_mw: float | None = Field(default=None, alias="sewa_mw", description="Kapasitas pembangkit sewa (Leased). Null jika \"-\"")
    ipp_mw: float | None = Field(default=None, alias="ipp_mw", description="Kapasitas pembangkit IPP. Null jika \"-\"")
    jumlah_mw: float | None = Field(default=None, alias="jumlah_mw", description="Jumlah total kapasitas (sub jumlah + sewa + IPP). Null jika \"-\"")
    jumlah_persen: float | None = Field(default=None, alias="jumlah_persen", description="Persentase jumlah terhadap total Indonesia. Null jika \"-\"")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
