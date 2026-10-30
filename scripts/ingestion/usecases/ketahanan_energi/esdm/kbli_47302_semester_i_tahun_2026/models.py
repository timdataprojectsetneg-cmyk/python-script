"""Pydantic schema — Daftar Penyalur Badan Usaha Niaga Umum Bahan Bakar Minyak melalui selain di Stasiun Pengisian (Agen BBM Industri) – KBLI 47302 Semester I Tahun 2026 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    no_badan_usaha: int | None = Field(default=None, alias="No. Badan Usaha", description="Nomor urut badan usaha niaga umum")
    nama_badan_usaha: str | None = Field(default=None, alias="Nama Badan Usaha", description="Nama badan usaha niaga umum BBM")
    no_penyalur: int | None = Field(default=None, alias="No. Penyalur", description="Nomor urut penyalur dalam badan usaha; null jika badan usaha tidak memiliki penyalur")
    nama_penyalur: str | None = Field(default=None, alias="Nama Penyalur", description="Nama penyalur BBM agen industri")
    alamat_kantor: str | None = Field(default=None, alias="Alamat Kantor", description="Alamat kantor penyalur sebagaimana tertulis di laporan")
    wilayah_penyaluran: str | None = Field(default=None, alias="Wilayah Penyaluran (Provinsi)", description="Wilayah penyaluran, dapat berisi beberapa provinsi/wilayah dalam satu teks")
    keterangan: str | None = Field(default=None, alias="Keterangan", description="Status badan usaha bila tidak memiliki penyalur, mis. TIDAK MEMILIKI PENYALUR, BELUM MELAPORKAN PENYALUR, atau sanksi")

    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}

