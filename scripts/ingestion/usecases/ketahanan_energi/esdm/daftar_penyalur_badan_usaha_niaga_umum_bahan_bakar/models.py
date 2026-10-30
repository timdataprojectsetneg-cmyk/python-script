"""Pydantic schema — Daftar Penyalur Badan Usaha Niaga Umum Bahan Bakar Minyak TW I Tahun 2025 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    no_badan_usaha: int | None = Field(default=None, alias="No. Badan Usaha", description="Nomor urut badan usaha niaga")
    nama_badan_usaha: str | None = Field(default=None, alias="Nama Badan Usaha", description="Nama badan usaha niaga")
    no_penyalur: int | None = Field(default=None, alias="No. Penyalur", description="Nomor urut penyalur dalam badan usaha")
    nama_penyalur: str | None = Field(default=None, alias="Nama Penyalur", description="Nama penyalur (agen/SPBU/SPBN/SPBKB)")
    bentuk_penyalur: str | None = Field(default=None, alias="Bentuk Penyalur", description="Bentuk penyalur: SPBU, SPBN, SPBKB, SPBKB (3T), dan sejenisnya")
    alamat_fasilitas: str | None = Field(default=None, alias="Alamat Fasilitas", description="Alamat fasilitas penyalur")
    nama_stasiun: str | None = Field(default=None, alias="Nama Stasiun", description="Nama stasiun pengisian BBM (SPBU BP ...). Hanya terisi untuk badan usaha yang mencantumkannya; null bila tidak ada")
    kota_kabupaten: str | None = Field(default=None, alias="Kota/Kabupaten", description="Kota/kabupaten lokasi fasilitas")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Provinsi lokasi fasilitas. Null bila dokumen tidak mencantumkan provinsi")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
