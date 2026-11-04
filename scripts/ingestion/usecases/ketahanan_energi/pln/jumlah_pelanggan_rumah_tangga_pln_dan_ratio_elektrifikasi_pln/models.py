"""Pydantic schema — Tabel Jumlah Pelanggan Rumah Tangga PLN dan Ratio Elektrifikasi PLN (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    sistem: str | None = Field(default=None, alias="Sistem", description="Sistem kelistrikan pada tabel sumber (contoh: Sumatera-Bangka)")
    skenario: str | None = Field(default=None, alias="Skenario", description="Skenario perencanaan: ARED atau RE Base")
    kelompok: str | None = Field(default=None, alias="Kelompok", description="Bagian tabel: Kebutuhan, Pasokan Eksisting, atau Rekapitulasi")
    uraian: str | None = Field(default=None, alias="Uraian", description="Nama indikator, misalnya Beban Puncak Neto, Total Daya Mampu Neto (DMN), atau Reserve Margin")
    satuan: str | None = Field(default=None, alias="Satuan", description="Satuan indikator: GWh, MW, atau %")
    2025_s_d_2034: str | None = Field(default=None, alias="2025 s.d. 2034", description="Nilai proyeksi per tahun (satu kolom per tahun")

    model_config = {"populate_by_name": True, "extra": "ignore"}

