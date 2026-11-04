"""Pydantic schema — PLN - Statistik PLN 2025 - Table 18 : Jumlah Gangguan Distribusi per 100 kms (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    unit_pln: str | None = Field(default=None, alias="Unit_PLN", description="Nama unit PLN, sub-unit provinsi (baris berawalan \"-\" di tabel sumber), atau baris agregat (Luar Jawa, Jawa, Indonesia)")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"unit\", \"sub_unit\" (bertanda \"-\" di sumber), \"subtotal_wilayah\", atau \"total\"")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2025)")
    unit_pln: str | None = Field(default=None, alias="unit_pln", description="Nama unit PLN, baris agregat \"Luar Jawa\" dan \"Jawa\", atau \"Indonesia\"")

    induk_unit: str | None = Field(default=None, alias="induk_unit", description="Nama unit induk untuk baris \"sub_unit\". Null untuk baris lain")
    kelompok_wilayah: str | None = Field(default=None, alias="kelompok_wilayah", description="Kelompok wilayah: \"Luar Jawa\" atau \"Jawa\". Null untuk baris total")
    jumlah_gangguan_kali: int | None = Field(default=None, alias="jumlah_gangguan_kali", description="Jumlah gangguan distribusi (Number of Interruption). Null jika \"-\"")
    panjang_jaringan_jtm_kms: float | None = Field(default=None, alias="panjang_jaringan_jtm_kms", description="Panjang jaringan Jaringan Tegangan Menengah (JTM). Null jika \"-\"")
    jumlah_gangguan_per_100kms: float | None = Field(default=None, alias="jumlah_gangguan_per_100kms", description="Jumlah gangguan per 100 kms jaringan JTM. Null jika \"-\"")
    model_config = {"populate_by_name": True, "extra": "ignore"}
