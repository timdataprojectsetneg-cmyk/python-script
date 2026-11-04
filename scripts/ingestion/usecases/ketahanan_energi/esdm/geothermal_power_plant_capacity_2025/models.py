"""Pydantic schema — 6.5.2 Geothermal Power Plant Capacity 2025 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data")
    kategori: str | None = Field(default=None, alias="kategori", description="Kategori (null pada dataset ini)")
    jenis_pembangkit: str | None = Field(default=None, alias="jenis_pembangkit", description="Nama pembangkit listrik tenaga panas bumi (PLTP)")
    nilai: str | None = Field(default=None, alias="nilai", description="Nilai kapasitas atau produksi")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai (mis. MW, TWh)")
    provinsi: str | None = Field(default=None, alias="provinsi", description="Provinsi lokasi PLTP")
    kode_provinsi: str | None = Field(default=None, alias="kode_provinsi", description="Kode wilayah Kemendagri (bisa null)")
    ipb_owner: str | None = Field(default=None, alias="ipb_owner", description="Pemilik/operator PLTP (bisa null)")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
