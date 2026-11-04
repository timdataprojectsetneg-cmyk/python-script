"""Pydantic schema — PPLN_Tabel Beban Pokok Penjualan (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    nilai: int | None = Field(default=None, alias="nilai", description="Arus kas pada tahun terkait. Negatif untuk nilai berkurung (arus keluar). Null jika sel di sumber kosong")

    aktivitas: str | None = Field(default=None, alias="aktivitas", description="Kelompok aktivitas arus kas: \"operasi\", \"investasi\", atau \"pendanaan\". Null untuk pos rekonsiliasi kas di akhir laporan (kenaikan bersih, saldo awal, efek kurs, saldo akhir)")
    kelompok: str | None = Field(default=None, alias="kelompok", description="Sub-kelompok di bawah aktivitas operasi: \"Penerimaan kas dari aktivitas operasi\" atau \"Pembayaran kas dari aktivitas operasi\". Null untuk pos lain")
    uraian: str | None = Field(default=None, alias="uraian", description="Nama pos arus kas (bahasa Indonesia)")
    uraian_en: str | None = Field(default=None, alias="uraian_en", description="Nama pos dalam bahasa Inggris sesuai sumber")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"item\" (pos biasa) atau \"total\" (kas diperoleh dari operasi, jumlah arus kas bersih per aktivitas, jumlah kenaikan bersih kas, saldo kas akhir periode)")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun laporan: 2025 atau 2024")
    model_config = {"populate_by_name": True, "extra": "ignore"}
