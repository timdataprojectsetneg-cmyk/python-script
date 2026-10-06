"""Pydantic schema — Kemnaker Perusahaan WLKP (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    no: int | None = Field(default=None, alias="No.", description="Nomor urut baris pada tabel")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi di Indonesia (38 provinsi); ada juga baris \"Tidak Teridentifikasi\" untuk perusahaan yang provinsinya tidak tercatat, dan baris \"Jumlah\" sebagai total nasional")
    mikro: int | None = Field(default=None, alias="Mikro", description="Jumlah perusahaan terlapor WLKP Online dengan skala usaha \"Mikro\" berdasarkan jumlah tenaga kerja, per provinsi")
    kecil: int | None = Field(default=None, alias="Kecil", description="Jumlah perusahaan terlapor WLKP Online dengan skala usaha \"Kecil\" berdasarkan jumlah tenaga kerja, per provinsi")
    menengah: int | None = Field(default=None, alias="Menengah", description="Jumlah perusahaan terlapor WLKP Online dengan skala usaha \"Menengah\" berdasarkan jumlah tenaga kerja, per provinsi")
    besar: int | None = Field(default=None, alias="Besar", description="Jumlah perusahaan terlapor WLKP Online dengan skala usaha \"Besar\" berdasarkan jumlah tenaga kerja, per provinsi")
    belum_teridentifikasi: int | None = Field(default=None, alias="Belum Teridentifikasi", description="Jumlah perusahaan terlapor yang skala usahanya (kategori Mikro/Kecil/Menengah/Besar) belum/tidak dapat diidentifikasi, per provinsi")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total perusahaan terlapor WLKP Online per provinsi (penjumlahan kolom Mikro + Kecil + Menengah + Besar + Belum Teridentifikasi)")

    model_config = {"populate_by_name": True, "extra": "ignore"}

