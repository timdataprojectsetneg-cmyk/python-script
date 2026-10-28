# Data Dictionary: Harga Brent Harian

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Harga Brent Harian`
- Publisher: EIA
- Data access: `excel`
- Update frequency: Harian (hari kerja)
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/eia/harga_brent_harian/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Day | `day` | Date | MM/DD/YYYY | Tanggal perdagangan (hari kerja). Format AS bulan/hari/tahun dengan hari tanpa nol di depan (mis. 10/9/2026) — wajib di-parse eksplisit ke YYYY-MM-DD, jangan diasumsikan DD/MM. |
| Europe Brent Spot Price FOB  Dollars per Barrel | `europe_brent_spot_price_fob_dollars_per_barrel` | Decimal | USD/barel | Harga spot minyak mentah Brent (FOB Eropa) harian. Dipakai untuk kartu harga Brent, sparkline, dan analisis skenario (tab Dampak). Nama kolom mengandung dua spasi; di CLEAN diganti menjadi brent_usd_per_bbl. |
| series_id* | `series_id` | String | Kode | Turunan dari URL pada baris metadata ke-2: RBRTE (harian; RBRTED.htm). Kunci bila menambah seri lain (WTI = RWTC). |
| source_vendor* | `source_vendor` | String | - | Turunan dari baris metadata ke-4: "Thomson Reuters" (penyedia data asli EIA). |

## Generated Pydantic model

```python
from datetime import date
from pydantic import BaseModel, Field


class HargaBrentHarianRecord(BaseModel):
    day: date | None = Field(default=None, alias="Day", description="Tanggal perdagangan (hari kerja). Format AS bulan/hari/tahun dengan hari tanpa nol di depan (mis. 10/9/2026) — wajib di-parse eksplisit ke YYYY-MM-DD, jangan diasumsikan DD/MM.")
    europe_brent_spot_price_fob_dollars_per_barrel: float | None = Field(default=None, alias="Europe Brent Spot Price FOB  Dollars per Barrel", description="Harga spot minyak mentah Brent (FOB Eropa) harian. Dipakai untuk kartu harga Brent, sparkline, dan analisis skenario (tab Dampak). Nama kolom mengandung dua spasi; di CLEAN diganti menjadi brent_usd_per_bbl.")
    series_id: str | None = Field(default=None, alias="series_id*", description="Turunan dari URL pada baris metadata ke-2: RBRTE (harian; RBRTED.htm). Kunci bila menambah seri lain (WTI = RWTC).")
    source_vendor: str | None = Field(default=None, alias="source_vendor*", description="Turunan dari baris metadata ke-4: \"Thomson Reuters\" (penyedia data asli EIA).")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
