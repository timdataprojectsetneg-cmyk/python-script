# Data Dictionary: PPLN_Tabel Beban Pokok Penjualan

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `PPLN_Tabel Beban Pokok Penjualan`
- Publisher: pln
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [PLN - Cost of Goods Sold](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Harga,%20Subsidi,%20dan%20Beban%20Fiskal%20Energi.xlsx?d=w8600be84249e4b8db4faec846dcce2da&csf=1&web=1&e=foIC2M&nav=MTVfezUzMkQ1MURBLThGMTUtNEYyQy04REU5LTQxNUVBRjI3NkMxM30)
- Target module: `ingestion/usecases/ketahanan_energi/pln/ppln_tabel_beban_pokok_penjualan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| aktivitas | `aktivitas` | string | - | Kelompok aktivitas arus kas: "operasi", "investasi", atau "pendanaan". Null untuk pos rekonsiliasi kas di akhir laporan (kenaikan bersih, saldo awal, efek kurs, saldo akhir) |
| kelompok | `kelompok` | string | - | Sub-kelompok di bawah aktivitas operasi: "Penerimaan kas dari aktivitas operasi" atau "Pembayaran kas dari aktivitas operasi". Null untuk pos lain |
| uraian | `uraian` | string | - | Nama pos arus kas (bahasa Indonesia) |
| uraian_en | `uraian_en` | string | - | Nama pos dalam bahasa Inggris sesuai sumber |
| tipe_baris | `tipe_baris` | string | - | Jenis baris: "item" (pos biasa) atau "total" (kas diperoleh dari operasi, jumlah arus kas bersih per aktivitas, jumlah kenaikan bersih kas, saldo kas akhir periode) |
| tahun | `tahun` | integer | Tahun | Tahun laporan: 2025 atau 2024 |
| nilai | `nilai` | integer | Rupiah juta | Arus kas pada tahun terkait. Negatif untuk nilai berkurung (arus keluar). Null jika sel di sumber kosong |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PplnTabelBebanPokokPenjualanRecord(BaseModel):
    aktivitas: str | None = Field(default=None, alias="aktivitas", description="Kelompok aktivitas arus kas: \"operasi\", \"investasi\", atau \"pendanaan\". Null untuk pos rekonsiliasi kas di akhir laporan (kenaikan bersih, saldo awal, efek kurs, saldo akhir)")
    kelompok: str | None = Field(default=None, alias="kelompok", description="Sub-kelompok di bawah aktivitas operasi: \"Penerimaan kas dari aktivitas operasi\" atau \"Pembayaran kas dari aktivitas operasi\". Null untuk pos lain")
    uraian: str | None = Field(default=None, alias="uraian", description="Nama pos arus kas (bahasa Indonesia)")
    uraian_en: str | None = Field(default=None, alias="uraian_en", description="Nama pos dalam bahasa Inggris sesuai sumber")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"item\" (pos biasa) atau \"total\" (kas diperoleh dari operasi, jumlah arus kas bersih per aktivitas, jumlah kenaikan bersih kas, saldo kas akhir periode)")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun laporan: 2025 atau 2024")
    nilai: int | None = Field(default=None, alias="nilai", description="Arus kas pada tahun terkait. Negatif untuk nilai berkurung (arus keluar). Null jika sel di sumber kosong")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
