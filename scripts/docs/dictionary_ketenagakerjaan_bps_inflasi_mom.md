# Data Dictionary: BPS Inflasi MoM

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketenagakerjaan`
- Source: `BPS Inflasi MoM`
- Publisher: BPS
- Data access: `api`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=zh2F9K&nav=MTVfezczOUE2QjcxLTA5QzktNDNGRS04NUFELUY1RDk3RjRENzIyMX0)
- Target module: `ingestion/usecases/ketenagakerjaan/bps/bps_inflasi_mom/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Kota_Inflasi | `kota_inflasi` | String | - | Nama kabupaten/kota yang menjadi titik pantau inflasi BPS (mengikuti daftar kota IHK yang dipakai BPS untuk hitung inflasi; bukan seluruh kabupaten/kota di Indonesia, hanya kota-kota sampel yang punya pos pemantauan harga BPS - isinya campuran kategori KAB dan KOTA). |
| Januari s.d. Desember (12 kolom terpisah per bulan) | `januari_s_d_desember_12_kolom_terpisah_per_bulan` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| Tahunan | `tahunan` | Decimal | Persen | Akumulasi inflasi tahun kalender (year-to-date, dari Januari s.d. bulan terakhir yang tersedia) - BUKAN inflasi year-on-year (data y-o-y ada di sheet terpisah "BPS Inflasi YOY"). Perlu dikonfirmasi ke definisi asli BPS untuk memastikan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsInflasiMomRecord(BaseModel):
    kota_inflasi: str | None = Field(default=None, alias="Kota_Inflasi")
    januari_s_d_desember_12_kolom_terpisah_per_bulan: float | None = Field(default=None, alias="Januari s.d. Desember (12 kolom terpisah per bulan)")
    tahunan: float | None = Field(default=None, alias="Tahunan")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
