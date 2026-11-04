"""Pydantic schema — Kinerja Penjualan Segmen Ritel, Kinerja Penjualan Segmen Korporat (mirrors the Data Dictionary)."""

from decimal import Decimal

from pydantic import BaseModel, Field


class Record(BaseModel):
    jenis_produk: str | None = Field(default=None, alias="Jenis Produk", description="Nama produk, kelompok produk, subtotal, atau total dalam tabel kinerja penjualan segmen. Ritel memuat BBM JBT, JBKP, JBU serta LPG PSO dan Non PSO; Korporat memuat BBM, Aviation Fuel Business, Petrokimia, dan Overseas. Baris Sub Jumlah dan Jumlah Volume Penjualan adalah agregat dan tidak boleh dijumlahkan kembali dengan komponen rinciannya.")
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun kalender yang menjadi periode pelaporan volume penjualan. Nilai 2024 dan 2025 merupakan periode observasi yang terpisah; satu baris mewakili satu kategori pasar atau produk pada satu tahun. Data ini tidak memiliki rincian bulanan atau harian.")
    kenaikan_penurunan_persen: Decimal | None = Field(default=None, alias="Kenaikan/Penurunan Persen", description="Persentase perubahan volume penjualan 2025 dibandingkan 2024 yang dilaporkan dalam tabel sumber. Nilai positif menunjukkan pertumbuhan dan nilai negatif menunjukkan penurunan. Diisi pada baris 2025 dan null pada baris 2024. Nilai dipertahankan sesuai publikasi, termasuk bila tidak konsisten dengan perhitungan perubahan absolut dibagi volume tahun sebelumnya.")

    segmen_pasar: str | None = Field(default=None, alias="Segmen Pasar", description="Klasifikasi pelanggan pada tabel kinerja penjualan: Ritel atau Korporat. Digunakan bersama Jenis Produk dan Tahun untuk membedakan observasi; nama produk yang sama pada dua segmen tidak merepresentasikan baris yang sama.")
    volume_penjualan: Decimal | None = Field(default=None, alias="Volume Penjualan", description="Volume penjualan yang dilaporkan untuk kategori pasar atau produk pada tahun terkait, dalam kilo liter (KL), bukan juta KL. Nilai dipertahankan sesuai tabel sumber dan tidak dihitung ulang dari subtotal. Baris total dan subtotal tidak boleh dijumlahkan kembali dengan baris rinciannya.")
    kontribusi: Decimal | None = Field(default=None, alias="Kontribusi", description="Persentase volume penjualan suatu kategori terhadap total yang digunakan dalam tabel sumber pada tahun terkait. Untuk dataset per pasar, acuannya total penjualan perusahaan; untuk dataset ritel/korporat, acuannya mengikuti tabel segmen. Nilai disalin dari sumber, bukan dihitung ulang; ketidaksesuaian aritmetika pada sumber tetap dipertahankan.")
    satuan_volume: str | None = Field(default=None, alias="Satuan Volume", description="Satuan untuk volume penjualan dan perubahan absolut volume, yaitu kilo liter (KL). Satu KL setara dengan 1.000 liter. Kolom ini tidak berlaku sebagai satuan kontribusi atau perubahan persentase, yang dinyatakan dalam persen.")
    kenaikan_penurunan_volume: Decimal | None = Field(default=None, alias="Kenaikan/Penurunan Volume", description="Perubahan absolut volume penjualan tahun 2025 terhadap 2024 dalam kilo liter (KL), sebagaimana tercantum dalam tabel sumber. Nilai positif menunjukkan kenaikan dan nilai negatif menunjukkan penurunan. Hanya diisi pada baris 2025; null pada baris 2024 berarti pembanding tidak tersedia, bukan perubahan nol. Angka sumber tidak dikoreksi otomatis meskipun berbeda dari hasil pengurangan.")
    model_config = {"populate_by_name": True, "extra": "ignore"}
