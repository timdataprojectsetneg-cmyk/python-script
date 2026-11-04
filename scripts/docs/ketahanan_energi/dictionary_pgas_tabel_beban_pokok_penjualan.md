# Data Dictionary: PGAS_Tabel Beban Pokok Penjualan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `PGAS_Tabel Beban Pokok Penjualan`
- Publisher: idx
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PGN - Cost of Goods Sold](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=d8U2Ef&nav=MTVfe0UyNUZCMzZBLTI2NTMtNDE0Ri05Mzk1LUU2Mjg1OTI5REYwOH0)
- Target module: `ingestion/usecases/ketahanan_energi/idx/pgas_tabel_beban_pokok_penjualan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| uraian | `uraian` | string | - | Nama pos beban pokok penjualan (bahasa Indonesia). Ejaan mengikuti sumber, misalnya "Biaya pabrikasi lainya" dan "Realti dan properti" |
| tipe_baris | `tipe_baris` | string | - | Jenis baris: "item" (pos biasa), "subtotal" (Bahan baku yang digunakan, Jumlah biaya produksi, Harga pokok produksi), atau "total" (Beban pokok penjualan dan pendapatan) |
| tahun | `tahun` | integer | Tahun | Tahun laporan: 2025 (31 Desember 2025) atau 2024 (31 Desember 2024) |
| nilai | `nilai` | integer | Rupiah juta | Nilai pos pada tahun terkait. Null jika sel di sumber kosong |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PgasTabelBebanPokokPenjualanRecord(BaseModel):
    uraian: str | None = Field(default=None, alias="uraian", description="Nama pos beban pokok penjualan (bahasa Indonesia). Ejaan mengikuti sumber, misalnya \"Biaya pabrikasi lainya\" dan \"Realti dan properti\"")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"item\" (pos biasa), \"subtotal\" (Bahan baku yang digunakan, Jumlah biaya produksi, Harga pokok produksi), atau \"total\" (Beban pokok penjualan dan pendapatan)")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun laporan: 2025 (31 Desember 2025) atau 2024 (31 Desember 2024)")
    nilai: int | None = Field(default=None, alias="nilai", description="Nilai pos pada tahun terkait. Null jika sel di sumber kosong")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
