"""Pydantic schema — Tabel  Nilai Energi Terpakai Untuk Produksi Listrik dari Pemakaian Sumber Energi (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai pada baris tersebut: \"GWh\" atau \"GJ\"")

    jenis_pemakaian: str | None = Field(default=None, alias="jenis_pemakaian", description="Jenis pemakaian sendiri listrik untuk operasional: \"Sentral Pembangkit (termasuk Susut Trafo Pembangkit)\", \"Gardu Induk\", \"Distribusi\", atau \"Total\"")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"item\" (jenis pemakaian) atau \"total\" (total keseluruhan)")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2023, 2024, 2025)")
    nilai: float | None = Field(default=None, alias="nilai", description="Besar pemakaian sendiri listrik untuk operasional pada jenis pemakaian, satuan, dan tahun terkait. Desimal untuk GWh, bilangan bulat untuk GJ")
    model_config = {"populate_by_name": True, "extra": "ignore"}
