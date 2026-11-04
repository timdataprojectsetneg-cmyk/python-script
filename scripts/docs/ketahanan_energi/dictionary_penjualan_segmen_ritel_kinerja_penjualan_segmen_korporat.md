# Data Dictionary: Kinerja Penjualan Segmen Ritel, Kinerja Penjualan Segmen Korporat

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Kinerja Penjualan Segmen Ritel, Kinerja Penjualan Segmen Korporat`
- Publisher: pertamina
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Pertamina_Penyaluran (Segmen)](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=iMlEVM&nav=MTVfezQ3RENBOTdELTc0RUItNDYxQy1BODI2LUZBQzg1NzE1OEMwN30)
- Target module: `ingestion/usecases/ketahanan_energi/pertamina/penjualan_segmen_ritel_kinerja_penjualan_segmen_korporat/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Segmen Pasar | `segmen_pasar` | Text | - | Klasifikasi pelanggan pada tabel kinerja penjualan: Ritel atau Korporat. Digunakan bersama Jenis Produk dan Tahun untuk membedakan observasi; nama produk yang sama pada dua segmen tidak merepresentasikan baris yang sama. |
| Jenis Produk | `jenis_produk` | Text | - | Nama produk, kelompok produk, subtotal, atau total dalam tabel kinerja penjualan segmen. Ritel memuat BBM JBT, JBKP, JBU serta LPG PSO dan Non PSO; Korporat memuat BBM, Aviation Fuel Business, Petrokimia, dan Overseas. Baris Sub Jumlah dan Jumlah Volume Penjualan adalah agregat dan tidak boleh dijumlahkan kembali dengan komponen rinciannya. |
| Tahun | `tahun` | Integer | Tahun | Tahun kalender yang menjadi periode pelaporan volume penjualan. Nilai 2024 dan 2025 merupakan periode observasi yang terpisah; satu baris mewakili satu kategori pasar atau produk pada satu tahun. Data ini tidak memiliki rincian bulanan atau harian. |
| Volume Penjualan | `volume_penjualan` | Decimal | Kilo Liter | Volume penjualan yang dilaporkan untuk kategori pasar atau produk pada tahun terkait, dalam kilo liter (KL), bukan juta KL. Nilai dipertahankan sesuai tabel sumber dan tidak dihitung ulang dari subtotal. Baris total dan subtotal tidak boleh dijumlahkan kembali dengan baris rinciannya. |
| Kontribusi | `kontribusi` | Decimal | Persen | Persentase volume penjualan suatu kategori terhadap total yang digunakan dalam tabel sumber pada tahun terkait. Untuk dataset per pasar, acuannya total penjualan perusahaan; untuk dataset ritel/korporat, acuannya mengikuti tabel segmen. Nilai disalin dari sumber, bukan dihitung ulang; ketidaksesuaian aritmetika pada sumber tetap dipertahankan. |
| Satuan Volume | `satuan_volume` | Text | - | Satuan untuk volume penjualan dan perubahan absolut volume, yaitu kilo liter (KL). Satu KL setara dengan 1.000 liter. Kolom ini tidak berlaku sebagai satuan kontribusi atau perubahan persentase, yang dinyatakan dalam persen. |
| Kenaikan/Penurunan Volume | `kenaikan_penurunan_volume` | Decimal | Kilo Liter | Perubahan absolut volume penjualan tahun 2025 terhadap 2024 dalam kilo liter (KL), sebagaimana tercantum dalam tabel sumber. Nilai positif menunjukkan kenaikan dan nilai negatif menunjukkan penurunan. Hanya diisi pada baris 2025; null pada baris 2024 berarti pembanding tidak tersedia, bukan perubahan nol. Angka sumber tidak dikoreksi otomatis meskipun berbeda dari hasil pengurangan. |
| Kenaikan/Penurunan Persen | `kenaikan_penurunan_persen` | Decimal | Persen | Persentase perubahan volume penjualan 2025 dibandingkan 2024 yang dilaporkan dalam tabel sumber. Nilai positif menunjukkan pertumbuhan dan nilai negatif menunjukkan penurunan. Diisi pada baris 2025 dan null pada baris 2024. Nilai dipertahankan sesuai publikasi, termasuk bila tidak konsisten dengan perhitungan perubahan absolut dibagi volume tahun sebelumnya. |

## Generated Pydantic model

```python
from decimal import Decimal
from pydantic import BaseModel, Field


class PenjualanSegmenRitelKinerjaPenjualanSegmenKorporatRecord(BaseModel):
    segmen_pasar: str | None = Field(default=None, alias="Segmen Pasar", description="Klasifikasi pelanggan pada tabel kinerja penjualan: Ritel atau Korporat. Digunakan bersama Jenis Produk dan Tahun untuk membedakan observasi; nama produk yang sama pada dua segmen tidak merepresentasikan baris yang sama.")
    jenis_produk: str | None = Field(default=None, alias="Jenis Produk", description="Nama produk, kelompok produk, subtotal, atau total dalam tabel kinerja penjualan segmen. Ritel memuat BBM JBT, JBKP, JBU serta LPG PSO dan Non PSO; Korporat memuat BBM, Aviation Fuel Business, Petrokimia, dan Overseas. Baris Sub Jumlah dan Jumlah Volume Penjualan adalah agregat dan tidak boleh dijumlahkan kembali dengan komponen rinciannya.")
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun kalender yang menjadi periode pelaporan volume penjualan. Nilai 2024 dan 2025 merupakan periode observasi yang terpisah; satu baris mewakili satu kategori pasar atau produk pada satu tahun. Data ini tidak memiliki rincian bulanan atau harian.")
    volume_penjualan: Decimal | None = Field(default=None, alias="Volume Penjualan", description="Volume penjualan yang dilaporkan untuk kategori pasar atau produk pada tahun terkait, dalam kilo liter (KL), bukan juta KL. Nilai dipertahankan sesuai tabel sumber dan tidak dihitung ulang dari subtotal. Baris total dan subtotal tidak boleh dijumlahkan kembali dengan baris rinciannya.")
    kontribusi: Decimal | None = Field(default=None, alias="Kontribusi", description="Persentase volume penjualan suatu kategori terhadap total yang digunakan dalam tabel sumber pada tahun terkait. Untuk dataset per pasar, acuannya total penjualan perusahaan; untuk dataset ritel/korporat, acuannya mengikuti tabel segmen. Nilai disalin dari sumber, bukan dihitung ulang; ketidaksesuaian aritmetika pada sumber tetap dipertahankan.")
    satuan_volume: str | None = Field(default=None, alias="Satuan Volume", description="Satuan untuk volume penjualan dan perubahan absolut volume, yaitu kilo liter (KL). Satu KL setara dengan 1.000 liter. Kolom ini tidak berlaku sebagai satuan kontribusi atau perubahan persentase, yang dinyatakan dalam persen.")
    kenaikan_penurunan_volume: Decimal | None = Field(default=None, alias="Kenaikan/Penurunan Volume", description="Perubahan absolut volume penjualan tahun 2025 terhadap 2024 dalam kilo liter (KL), sebagaimana tercantum dalam tabel sumber. Nilai positif menunjukkan kenaikan dan nilai negatif menunjukkan penurunan. Hanya diisi pada baris 2025; null pada baris 2024 berarti pembanding tidak tersedia, bukan perubahan nol. Angka sumber tidak dikoreksi otomatis meskipun berbeda dari hasil pengurangan.")
    kenaikan_penurunan_persen: Decimal | None = Field(default=None, alias="Kenaikan/Penurunan Persen", description="Persentase perubahan volume penjualan 2025 dibandingkan 2024 yang dilaporkan dalam tabel sumber. Nilai positif menunjukkan pertumbuhan dan nilai negatif menunjukkan penurunan. Diisi pada baris 2025 dan null pada baris 2024. Nilai dipertahankan sesuai publikasi, termasuk bila tidak konsisten dengan perhitungan perubahan absolut dibagi volume tahun sebelumnya.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
