"""Pydantic schema — Tabel 17 Kuota dan Realisasi LPG Tabung 3 kg (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    komponen: str | None = Field(default=None, alias="komponen", description="Kuota LPG Tabung 3 kg, Realisasi LPG Tabung 3 kg, atau Persentase Realisasi")
    nilai: str | None = Field(default=None, alias="nilai", description="Kuota dan realisasi dalam Juta MT; persentase realisasi dalam %")
    satuan: str | None = Field(default=None, alias="satuan", description="Juta MT atau % (sesuai komponen)")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

