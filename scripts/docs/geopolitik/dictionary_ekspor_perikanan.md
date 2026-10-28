# Data Dictionary: Ekspor Perikanan KKP

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Ekspor Perikanan KKP`
- Publisher: KKP
- Data access: `scraper`
- Update frequency: Tahunan; 2026 berjalan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/kkp/ekspor_perikanan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Komoditas | `komoditas` | String | - | Kelompok komoditas hasil perikanan pada tabel KKP. |
| 2019 | `2019` | Decimal | Ribu USD | Nilai ekspor tahun 2019; 2026 merupakan data tahun berjalan pada tanggal rilis. |
| 2020 | `2020` | Decimal | Ribu USD | Nilai ekspor tahun 2020; 2026 merupakan data tahun berjalan pada tanggal rilis. |
| 2021 | `2021` | Decimal | Ribu USD | Nilai ekspor tahun 2021; 2026 merupakan data tahun berjalan pada tanggal rilis. |
| 2022 | `2022` | Decimal | Ribu USD | Nilai ekspor tahun 2022; 2026 merupakan data tahun berjalan pada tanggal rilis. |
| 2023 | `2023` | Decimal | Ribu USD | Nilai ekspor tahun 2023; 2026 merupakan data tahun berjalan pada tanggal rilis. |
| 2024 | `2024` | Decimal | Ribu USD | Nilai ekspor tahun 2024; 2026 merupakan data tahun berjalan pada tanggal rilis. |
| 2025 | `2025` | Decimal | Ribu USD | Nilai ekspor tahun 2025; 2026 merupakan data tahun berjalan pada tanggal rilis. |
| 2026 | `2026` | Decimal | Ribu USD | Nilai ekspor tahun 2026; 2026 merupakan data tahun berjalan pada tanggal rilis. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class EksporPerikananKkpRecord(BaseModel):
    komoditas: str | None = Field(default=None, alias="Komoditas", description="Kelompok komoditas hasil perikanan pada tabel KKP.")
    2019: float | None = Field(default=None, alias="2019", description="Nilai ekspor tahun 2019; 2026 merupakan data tahun berjalan pada tanggal rilis.")
    2020: float | None = Field(default=None, alias="2020", description="Nilai ekspor tahun 2020; 2026 merupakan data tahun berjalan pada tanggal rilis.")
    2021: float | None = Field(default=None, alias="2021", description="Nilai ekspor tahun 2021; 2026 merupakan data tahun berjalan pada tanggal rilis.")
    2022: float | None = Field(default=None, alias="2022", description="Nilai ekspor tahun 2022; 2026 merupakan data tahun berjalan pada tanggal rilis.")
    2023: float | None = Field(default=None, alias="2023", description="Nilai ekspor tahun 2023; 2026 merupakan data tahun berjalan pada tanggal rilis.")
    2024: float | None = Field(default=None, alias="2024", description="Nilai ekspor tahun 2024; 2026 merupakan data tahun berjalan pada tanggal rilis.")
    2025: float | None = Field(default=None, alias="2025", description="Nilai ekspor tahun 2025; 2026 merupakan data tahun berjalan pada tanggal rilis.")
    2026: float | None = Field(default=None, alias="2026", description="Nilai ekspor tahun 2026; 2026 merupakan data tahun berjalan pada tanggal rilis.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
