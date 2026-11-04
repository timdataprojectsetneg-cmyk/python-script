"""Pydantic schema — 6.2.1 Oil Reserves (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    kategori: str | None = Field(default=None, alias="kategori", description="Cadangan  (P1 + P2 + P3)")
    nilai: str | None = Field(default=None, alias="nilai", description="nilai cadangan pada wilayah")
    satuan: str | None = Field(default=None, alias="satuan", description="Total cadangan pada wilayah bersangkutan (P1 + P2 + P3)")

    tahun_number_kategori_string_wilayah_string_nilai_number_satuan_string: float | None = Field(default=None, alias="tahun (number), kategori (string), wilayah (string), nilai (number), satuan (string)", description="Tahun cadangan pada wilayah")
    wilayah: str | None = Field(default=None, alias="wilayah", description="Wilayah cadangan minyak bumi; pembagian wilayah tidak berdasarkan batas administratif. Baris Total untuk agregat nasional")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
