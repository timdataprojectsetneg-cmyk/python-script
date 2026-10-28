# Data Dictionary: Stabilitas Politik WGI

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Stabilitas Politik WGI`
- Publisher: World Bank
- Data access: `excel`
- Update frequency: Tahunan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Hubungan Bilateral (1).xlsx
- Target module: `ingestion/usecases/geopolitik/world_bank/stabilitas_politik_wgi/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Country Name | `country_name` | String | - | Nama negara/ekonomi atau agregat (bahasa Inggris, mis. "Iran, Islamic Rep."). |
| Country Code | `country_code` | String | ISO3 | Kode ISO 3166-1 alpha-3 / kode agregat World Bank. Kunci join ke ref_negara. 49 dari 266 baris adalah agregat (kawasan/kelompok pendapatan, mis. AFE, EAS) — Region kosong di file metadata; buang sebelum dipakai per negara. |
| Indicator Name | `indicator_name` | String | - | Nama indikator: "Political Stability - Governance estimate (approx. -2.5 to +2.5)". Konstan untuk satu file. |
| Indicator Code | `indicator_code` | String | Kode | GOV_WGI_PV_EST. Dimensi WGI lain memakai pola kode sama (GOV_WGI_VA/GE/RQ/RL/CC_EST) dan peringkat persentil memakai akhiran _PER_RNK (perlu file terpisah). |
| 1960 … 1995 | `1960_1995` | Decimal | Skor -2,5 s.d. +2,5 | Kolom tahun format lebar. Seluruhnya kosong — WGI baru mulai 1996. |
| 1996, 1998, 2000, 2002 … 2025 | `1996_1998_2000_2002_2025` | Decimal | Skor -2,5 s.d. +2,5 | Skor stabilitas politik & tidak adanya kekerasan/terorisme (persepsi). Makin tinggi makin stabil. 1997, 1999, 2001 kosong (WGI dua tahunan sebelum 2002). Tahun terbaru 2025 (207 negara/ekonomi terisi). |
| Region (file Metadata_Country) | `region_file_metadata_country` | String | - | Kawasan World Bank (mis. East Asia & Pacific). Kosong = baris agregat. |
| IncomeGroup (file Metadata_Country) | `incomegroup_file_metadata_country` | String | - | Kelompok pendapatan (High/Upper middle/Lower middle/Low income). |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class StabilitasPolitikWgiRecord(BaseModel):
    country_name: str | None = Field(default=None, alias="Country Name", description="Nama negara/ekonomi atau agregat (bahasa Inggris, mis. \"Iran, Islamic Rep.\").")
    country_code: str | None = Field(default=None, alias="Country Code", description="Kode ISO 3166-1 alpha-3 / kode agregat World Bank. Kunci join ke ref_negara. 49 dari 266 baris adalah agregat (kawasan/kelompok pendapatan, mis. AFE, EAS) — Region kosong di file metadata; buang sebelum dipakai per negara.")
    indicator_name: str | None = Field(default=None, alias="Indicator Name", description="Nama indikator: \"Political Stability - Governance estimate (approx. -2.5 to +2.5)\". Konstan untuk satu file.")
    indicator_code: str | None = Field(default=None, alias="Indicator Code", description="GOV_WGI_PV_EST. Dimensi WGI lain memakai pola kode sama (GOV_WGI_VA/GE/RQ/RL/CC_EST) dan peringkat persentil memakai akhiran _PER_RNK (perlu file terpisah).")
    1960_1995: float | None = Field(default=None, alias="1960 … 1995", description="Kolom tahun format lebar. Seluruhnya kosong — WGI baru mulai 1996.")
    1996_1998_2000_2002_2025: float | None = Field(default=None, alias="1996, 1998, 2000, 2002 … 2025", description="Skor stabilitas politik & tidak adanya kekerasan/terorisme (persepsi). Makin tinggi makin stabil. 1997, 1999, 2001 kosong (WGI dua tahunan sebelum 2002). Tahun terbaru 2025 (207 negara/ekonomi terisi).")
    region_file_metadata_country: str | None = Field(default=None, alias="Region (file Metadata_Country)", description="Kawasan World Bank (mis. East Asia & Pacific). Kosong = baris agregat.")
    incomegroup_file_metadata_country: str | None = Field(default=None, alias="IncomeGroup (file Metadata_Country)", description="Kelompok pendapatan (High/Upper middle/Lower middle/Low income).")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
