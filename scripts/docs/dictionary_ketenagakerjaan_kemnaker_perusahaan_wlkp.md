# Data Dictionary: Kemnaker Perusahaan WLKP

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `Kemnaker Perusahaan WLKP`
- Publisher: Kemnaker
- Data access: `excel`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=COIu0t&nav=MTVfezhCOTcwMUNGLUUyODgtNEY4Ni1CQkUxLUMyNENEQTc1QjQwMH0)
- Target module: `ingestion/usecases/ketenagakerjaan/kemnaker/kemnaker_perusahaan_wlkp/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| No. | `no` | Integer | - | Nomor urut baris pada tabel |
| Provinsi | `provinsi` | Text | - | Nama provinsi di Indonesia (38 provinsi); ada juga baris "Tidak Teridentifikasi" untuk perusahaan yang provinsinya tidak tercatat, dan baris "Jumlah" sebagai total nasional |
| Mikro | `mikro` | Integer | Perusahaan | Jumlah perusahaan terlapor WLKP Online dengan skala usaha "Mikro" berdasarkan jumlah tenaga kerja, per provinsi |
| Kecil | `kecil` | Integer | Perusahaan | Jumlah perusahaan terlapor WLKP Online dengan skala usaha "Kecil" berdasarkan jumlah tenaga kerja, per provinsi |
| Menengah | `menengah` | Integer | Perusahaan | Jumlah perusahaan terlapor WLKP Online dengan skala usaha "Menengah" berdasarkan jumlah tenaga kerja, per provinsi |
| Besar | `besar` | Integer | Perusahaan | Jumlah perusahaan terlapor WLKP Online dengan skala usaha "Besar" berdasarkan jumlah tenaga kerja, per provinsi |
| Belum Teridentifikasi | `belum_teridentifikasi` | Integer | Perusahaan | Jumlah perusahaan terlapor yang skala usahanya (kategori Mikro/Kecil/Menengah/Besar) belum/tidak dapat diidentifikasi, per provinsi |
| Jumlah | `jumlah` | Integer | Perusahaan | Total perusahaan terlapor WLKP Online per provinsi (penjumlahan kolom Mikro + Kecil + Menengah + Besar + Belum Teridentifikasi) |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class KemnakerPerusahaanWlkpRecord(BaseModel):
    no: int | None = Field(default=None, alias="No.", description="Nomor urut baris pada tabel")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi di Indonesia (38 provinsi); ada juga baris \"Tidak Teridentifikasi\" untuk perusahaan yang provinsinya tidak tercatat, dan baris \"Jumlah\" sebagai total nasional")
    mikro: int | None = Field(default=None, alias="Mikro", description="Jumlah perusahaan terlapor WLKP Online dengan skala usaha \"Mikro\" berdasarkan jumlah tenaga kerja, per provinsi")
    kecil: int | None = Field(default=None, alias="Kecil", description="Jumlah perusahaan terlapor WLKP Online dengan skala usaha \"Kecil\" berdasarkan jumlah tenaga kerja, per provinsi")
    menengah: int | None = Field(default=None, alias="Menengah", description="Jumlah perusahaan terlapor WLKP Online dengan skala usaha \"Menengah\" berdasarkan jumlah tenaga kerja, per provinsi")
    besar: int | None = Field(default=None, alias="Besar", description="Jumlah perusahaan terlapor WLKP Online dengan skala usaha \"Besar\" berdasarkan jumlah tenaga kerja, per provinsi")
    belum_teridentifikasi: int | None = Field(default=None, alias="Belum Teridentifikasi", description="Jumlah perusahaan terlapor yang skala usahanya (kategori Mikro/Kecil/Menengah/Besar) belum/tidak dapat diidentifikasi, per provinsi")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total perusahaan terlapor WLKP Online per provinsi (penjumlahan kolom Mikro + Kecil + Menengah + Besar + Belum Teridentifikasi)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
