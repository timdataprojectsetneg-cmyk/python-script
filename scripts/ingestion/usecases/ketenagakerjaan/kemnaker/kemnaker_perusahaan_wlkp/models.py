"""Pydantic schema — Kemnaker Perusahaan WLKP (mirrors the Data Dictionary).

Parsed by ``excel_automation`` (output ``data``): the flattened header yields
``skala_perusahaan_mikro``/``..._kecil``/``..._menengah``/``..._besar``/
``..._belum_teridentifikasi`` for the ``Skala Perusahaan`` group.
"""

from pydantic import BaseModel, Field


class Record(BaseModel):
    no: int | None = Field(default=None, alias="no", description="Nomor urut baris pada tabel.")
    provinsi: str | None = Field(
        default=None, alias="provinsi",
        description="Nama provinsi (38 provinsi), plus baris \"Tidak Teridentifikasi\" dan \"Jumlah\" (total nasional).",
    )
    mikro: int | None = Field(default=None, alias="skala_perusahaan_mikro", description="Jumlah perusahaan skala Mikro.")
    kecil: int | None = Field(default=None, alias="skala_perusahaan_kecil", description="Jumlah perusahaan skala Kecil.")
    menengah: int | None = Field(default=None, alias="skala_perusahaan_menengah", description="Jumlah perusahaan skala Menengah.")
    besar: int | None = Field(default=None, alias="skala_perusahaan_besar", description="Jumlah perusahaan skala Besar.")
    belum_teridentifikasi: int | None = Field(
        default=None, alias="skala_perusahaan_belum_teridentifikasi",
        description="Jumlah perusahaan yang skala usahanya belum/tidak teridentifikasi.",
    )
    jumlah: int | None = Field(default=None, alias="jumlah", description="Total perusahaan terlapor per baris.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
