"""Pydantic schema — Penyalur BBM PT ExxonMobil Lubricants Indonesia (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    nama_penyalur: str | None = Field(default=None, alias="Nama Penyalur", description="Nama badan usaha penyalur BBM")
    alamat_penyalur: str | None = Field(default=None, alias="Alamat Penyalur", description="Alamat penyalur sebagaimana tertulis di laporan")
    wilayah_penyaluran: str | None = Field(default=None, alias="Wilayah Penyaluran", description="Provinsi wilayah penyaluran penyalur agen BBM industri (KBLI 47302); satu record per provinsi. Null untuk baris microsite")
    nomor_microsite: str | None = Field(default=None, alias="Nomor Microsite", description="Nomor microsite sarana fasilitas penyalur, mis. 1223-31004. Null untuk baris wilayah penyaluran")
    kota_kabupaten: str | None = Field(default=None, alias="Kota/Kabupaten", description="Kota/kabupaten lokasi microsite. Null untuk baris wilayah penyaluran")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Provinsi lokasi microsite. Null untuk baris wilayah penyaluran")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
