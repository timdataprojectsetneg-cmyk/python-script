"""Pydantic schema for BP2MI Penempatan PMI (per negara, per bulan)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PenempatanPmiRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    tahun: Optional[int] = Field(
        default=None,
        alias="Tahun",
        description="Tahun laporan (dibaca dari judul tabel PDF).",
    )
    negara: Optional[str] = Field(
        default=None,
        alias="NEGARA",
        description="Negara/ekonomi sebagaimana tabel BP2MI; Lainnya adalah agregat negara di luar daftar.",
    )
    jan: Optional[int] = Field(
        default=None,
        alias="JAN",
        ge=0,
        description="Layanan penempatan bulan JAN; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    feb: Optional[int] = Field(
        default=None,
        alias="FEB",
        ge=0,
        description="Layanan penempatan bulan FEB; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    mar: Optional[int] = Field(
        default=None,
        alias="MAR",
        ge=0,
        description="Layanan penempatan bulan MAR; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    apr: Optional[int] = Field(
        default=None,
        alias="APR",
        ge=0,
        description="Layanan penempatan bulan APR; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    mei: Optional[int] = Field(
        default=None,
        alias="MEI",
        ge=0,
        description="Layanan penempatan bulan MEI; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    jun: Optional[int] = Field(
        default=None,
        alias="JUN",
        ge=0,
        description="Layanan penempatan bulan JUN; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    jul: Optional[int] = Field(
        default=None,
        alias="JUL",
        ge=0,
        description="Layanan penempatan bulan JUL; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    agu: Optional[int] = Field(
        default=None,
        alias="AGU",
        ge=0,
        description="Layanan penempatan bulan AGU; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    sep: Optional[int] = Field(
        default=None,
        alias="SEP",
        ge=0,
        description="Layanan penempatan bulan SEP; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    okt: Optional[int] = Field(
        default=None,
        alias="OKT",
        ge=0,
        description="Layanan penempatan bulan OKT; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    nov: Optional[int] = Field(
        default=None,
        alias="NOV",
        ge=0,
        description="Layanan penempatan bulan NOV; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    des: Optional[int] = Field(
        default=None,
        alias="DES",
        ge=0,
        description="Layanan penempatan bulan DES; kosong jika bulan belum dilaporkan, 0 berasal dari sumber.",
    )
    jumlah: Optional[int] = Field(
        default=None,
        alias="JUMLAH",
        ge=0,
        description="Jumlah Januari-Desember sebagaimana kolom JUMLAH sumber.",
    )
    halaman_pdf: Optional[int] = Field(
        default=None,
        alias="Halaman PDF",
        description="Halaman PDF tempat baris tabel berada.",
    )

Record = PenempatanPmiRecord
