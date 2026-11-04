"""Pydantic schema — Natural Gas and Products (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Produksi, Ekspor, atau Pemanfaatan (pemanfaatan gas per sektor, Gambar 6)")
    nilai: str | None = Field(default=None, alias="nilai", description="Nilai indikator. Kosong untuk sektor pemanfaatan yang hanya punya persentase")
    satuan: str | None = Field(default=None, alias="satuan", description="MMSCFD, TBTU")

    indikator: str | None = Field(default=None, alias="indikator", description="Nama indikator, mis. produksi gas, ekspor gas pipa, produksi LNG domestik, ekspor LNG, atau sektor pemanfaatan")
    pangsa_persen: str | None = Field(default=None, alias="pangsa_persen", description="Porsi sektor terhadap total pemanfaatan gas (diagram donat)")
    pertumbuhan_yoy_persen: str | None = Field(default=None, alias="pertumbuhan_yoy_persen", description="Pertumbuhan dibanding tahun sebelumnya, dari teks")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
