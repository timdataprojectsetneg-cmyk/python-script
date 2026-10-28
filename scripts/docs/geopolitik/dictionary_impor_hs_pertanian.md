# Data Dictionary: Impor HS Pertanian

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `geopolitik`
- Source: `Impor HS Pertanian`
- Publisher: Kementan
- Data access: `scraper`
- Update frequency: Bulanan
- Eligible: `True`
- Data Dictionary file: Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional (1).xlsx
- Target module: `ingestion/usecases/geopolitik/pertanian/impor_hs_pertanian/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Tahun | `tahun` | Integer | Tahun | Tahun observasi. |
| Arus | `arus` | String | Ekspor/Impor | Arah perdagangan. |
| Subsektor | `subsektor` | String | - | Subsektor yang dipilih pada query. |
| Kelompok Komoditas | `kelompok_komoditas` | String | - | Kelompok komoditas pada tabel sumber. |
| Kode HS | `kode_hs` | String | HS | Kode Harmonized System; disimpan sebagai teks agar nol awal tidak hilang. |
| Deskripsi HS | `deskripsi_hs` | String | - | Deskripsi barang pada portal. |
| Nomor Bulan | `nomor_bulan` | Integer | Bulan | Nomor 1–12 untuk pengurutan. |
| Bulan | `bulan` | String | - | Nama bulan dalam Bahasa Indonesia. |
| Volume | `volume` | Decimal | Kg | Volume perdagangan bulan tersebut. |
| Nilai | `nilai` | Decimal | USD | Nilai perdagangan bulan tersebut. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class ImporHsPertanianRecord(BaseModel):
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun observasi.")
    arus: str | None = Field(default=None, alias="Arus", description="Arah perdagangan.")
    subsektor: str | None = Field(default=None, alias="Subsektor", description="Subsektor yang dipilih pada query.")
    kelompok_komoditas: str | None = Field(default=None, alias="Kelompok Komoditas", description="Kelompok komoditas pada tabel sumber.")
    kode_hs: str | None = Field(default=None, alias="Kode HS", description="Kode Harmonized System; disimpan sebagai teks agar nol awal tidak hilang.")
    deskripsi_hs: str | None = Field(default=None, alias="Deskripsi HS", description="Deskripsi barang pada portal.")
    nomor_bulan: int | None = Field(default=None, alias="Nomor Bulan", description="Nomor 1–12 untuk pengurutan.")
    bulan: str | None = Field(default=None, alias="Bulan", description="Nama bulan dalam Bahasa Indonesia.")
    volume: float | None = Field(default=None, alias="Volume", description="Volume perdagangan bulan tersebut.")
    nilai: float | None = Field(default=None, alias="Nilai", description="Nilai perdagangan bulan tersebut.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
