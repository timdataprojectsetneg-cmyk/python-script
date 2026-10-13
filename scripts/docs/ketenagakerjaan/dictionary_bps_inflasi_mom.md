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
| Januari | `januari` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| februari | `februari` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| maret | `maret` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| april | `april` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| mei | `mei` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| juni | `juni` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| juli | `juli` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| agustus | `agustus` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| september | `september` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| oktober | `oktober` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| november | `november` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| desember | `desember` | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| Tahun | `tahun` | Decimal | Persen | Akumulasi inflasi tahun kalender (year-to-date, dari Januari s.d. bulan terakhir yang tersedia) - BUKAN inflasi year-on-year (data y-o-y ada di sheet terpisah "BPS Inflasi YOY"). Perlu dikonfirmasi ke definisi asli BPS untuk memastikan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsInflasiMomRecord(BaseModel):
    kota_inflasi: str | None = Field(default=None, alias="Kota_Inflasi", description="Nama kabupaten/kota yang menjadi titik pantau inflasi BPS (mengikuti daftar kota IHK yang dipakai BPS untuk hitung inflasi; bukan seluruh kabupaten/kota di Indonesia, hanya kota-kota sampel yang punya pos pemantauan harga BPS - isinya campuran kategori KAB dan KOTA).")
    januari: float | None = Field(default=None, alias="Januari", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    februari: float | None = Field(default=None, alias="februari", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    maret: float | None = Field(default=None, alias="maret", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    april: float | None = Field(default=None, alias="april", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    mei: float | None = Field(default=None, alias="mei", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    juni: float | None = Field(default=None, alias="juni", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    juli: float | None = Field(default=None, alias="juli", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    agustus: float | None = Field(default=None, alias="agustus", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    september: float | None = Field(default=None, alias="september", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    oktober: float | None = Field(default=None, alias="oktober", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    november: float | None = Field(default=None, alias="november", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    desember: float | None = Field(default=None, alias="desember", description="Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda \"-\" berarti data bulan tersebut belum dirilis BPS.")
    tahun: float | None = Field(default=None, alias="Tahun", description="Akumulasi inflasi tahun kalender (year-to-date, dari Januari s.d. bulan terakhir yang tersedia) - BUKAN inflasi year-on-year (data y-o-y ada di sheet terpisah \"BPS Inflasi YOY\"). Perlu dikonfirmasi ke definisi asli BPS untuk memastikan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
