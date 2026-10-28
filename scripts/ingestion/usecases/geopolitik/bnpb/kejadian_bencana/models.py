"""Pydantic schema mirroring the Data Dictionary for BNPB Kejadian Bencana."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BnpbKejadianBencanaRecord(BaseModel):
    no: Optional[int] = Field(default=None, alias="No.", description="Nomor urut baris hasil unduhan (bukan ID kejadian).")
    kode_identitas_bencana: Optional[str] = Field(default=None, alias="Kode Identitas Bencana", description="Kode identitas kejadian BNPB (sering kosong).")
    id_kabupaten: Optional[int] = Field(default=None, alias="ID Kabupaten", description="Kode kabupaten/kota 4 digit (Kemendagri/BPS).")
    tanggal_kejadian: dt.date = Field(alias="Tanggal Kejadian", description="Tanggal kejadian (tanpa jam).")
    kejadian: Optional[str] = Field(default=None, alias="Kejadian", description="Jenis bencana (huruf kapital).")
    lokasi: Optional[str] = Field(default=None, alias="Lokasi", description="Kecamatan/desa terdampak, teks bebas.")
    kabupaten: Optional[str] = Field(default=None, alias="Kabupaten", description="Nama kabupaten/kota.")
    provinsi: Optional[str] = Field(default=None, alias="Provinsi", description="Nama provinsi.")
    kronologi_dokumentasi: Optional[str] = Field(default=None, alias="Kronologi & Dokumentasi", description="Kronologi / tautan dokumentasi.")
    penyebab: Optional[str] = Field(default=None, alias="Penyebab", description="Penyebab kejadian.")
    meninggal: Optional[int] = Field(default=None, alias="Meninggal", description="Korban meninggal (orang); kosong = tidak dilaporkan.")
    hilang: Optional[int] = Field(default=None, alias="Hilang", description="Korban hilang (orang).")
    terluka: Optional[int] = Field(default=None, alias="Terluka", description="Korban luka (orang).")
    rumah_rusak: Optional[int] = Field(default=None, alias="Rumah Rusak", description="Rumah rusak (unit, gabungan).")
    rumah_terendam: Optional[int] = Field(default=None, alias="Rumah Terendam", description="Rumah terendam (unit).")
    fasum_rusak: Optional[int] = Field(default=None, alias="Fasum Rusak", description="Fasilitas umum rusak (unit).")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = BnpbKejadianBencanaRecord
