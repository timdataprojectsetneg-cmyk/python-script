"""Pydantic schema — Gambar 25 Peta Rencana Induk Jaringan Transmisi dan Distribusi gas Bumi  Nasional (RIJTDGBN) (mirrors the Data Dictionary)."""

from datetime import date
from pydantic import BaseModel, Field


class Record(BaseModel):

    kategori_infrastruktur: str | None = Field(default=None, alias="kategori_infrastruktur", description="Jenis infrastruktur pada legenda: Pipa Transmisi, Pipa Distribusi, Pipa Kepentingan Sendiri, FSRU/FRU/FSU, Kilang LNG, Fasilitas CNG, Terminal Penerima LNG Onshore, Wilayah Jaringan Distribusi, Jargas Rumah Tangga")
    status_pembangunan: str | None = Field(default=None, alias="status_pembangunan", description="Eksisting / Ongoing / Rencana, sesuai warna dan gaya garis pada legenda. Wilayah Jaringan Distribusi tidak punya status pada legenda")
    tipe_geometri: str | None = Field(default=None, alias="tipe_geometri", description="Garis (pipa), Titik (fasilitas, terminal, kilang, FSRU, CNG), atau Poligon (wilayah jaringan, jargas). Diturunkan dari simbol legenda, jadi perlu dicek ke data GIS asli")
    simbol_legenda: str | None = Field(default=None, alias="simbol_legenda", description="Deskripsi tampilan simbol pada legenda (warna, gaya garis/ikon) untuk tiap kategori dan status")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
