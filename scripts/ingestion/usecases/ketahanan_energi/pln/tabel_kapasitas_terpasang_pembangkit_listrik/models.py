"""Pydantic schema — Tabel Kapasitas Terpasang Pembangkit Listrik (MW) (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    regional: str | None = Field(default=None, alias="Regional", description="Wilayah regional PLN (misal: Sumatera dan Kalimantan; Jawa, Madura, dan Bali; Sulawesi, Maluku, Papua, dan Nusa Tenggara) beserta baris total (Jumlah SAIDI)")
    tahun: str | None = Field(default=None, alias="Tahun", description="Tahun pengukuran SAIDI (2023, 2024, 2025)")
    saidi: float | None = Field(default=None, alias="SAIDI", description="Rata-rata durasi gangguan listrik yang dialami setiap pelanggan dalam satu tahun pada regional tersebut")
    selisih: float | None = Field(default=None, alias="Selisih", description="Selisih perubahan SAIDI antara tahun 2024 dan 2025 (2025 - 2024). Nilai negatif berarti durasi gangguan berkurang (keandalan membaik). Hanya terisi pada baris tahun 2025; tahun lain null")
    persentase: str | None = Field(default=None, alias="Persentase", description="Persentase perubahan SAIDI dari tahun 2024 ke 2025. Nilai negatif berarti penurunan. Hanya terisi pada baris tahun 2025; tahun lain null")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Tipe baris: detail (data per regional) atau total (Jumlah SAIDI nasional)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
