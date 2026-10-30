"""Pydantic schema — Coal (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun neraca batubara (grafik 2019–2025)")
    komponen: str | None = Field(default=None, alias="komponen", description="Production, Export, Import, atau Domestic (penjualan domestik)")
    volume: str | None = Field(default=None, alias="volume", description="Volume per komponen. Export digambar di bawah sumbu nol dan ditulis dalam kurung, jadi bertanda negatif di grafik")
    pertumbuhan_yoy_persen: str | None = Field(default=None, alias="pertumbuhan_yoy_persen", description="Pertumbuhan dibanding tahun sebelumnya, dari teks. Kosong bila tidak disebut")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

