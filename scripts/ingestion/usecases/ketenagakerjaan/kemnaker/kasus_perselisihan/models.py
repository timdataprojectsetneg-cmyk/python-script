"""Pydantic schema — Kasus Perselisihan (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    jenis_perselisihan: str | None = Field(default=None, alias="Jenis_Perselisihan", description="Perselisihan Hak / Kepentingan / PHK / Serikat Pekerja.")
    jumlah_pusat: int | None = Field(default=None, alias="Jumlah_Pusat", description="Jumlah perselisihan tercatat di tingkat pusat.")
    jumlah_daerah: int | None = Field(default=None, alias="Jumlah_Daerah", description="Jumlah perselisihan tercatat di tingkat daerah.")
    bipartit_mediasi_pb_mediasi_anjuran_konsiliasi_arbitrasi_hakim_hi: int | None = Field(default=None, alias="Bipartit/Mediasi_PB/Mediasi_Anjuran/Konsiliasi/Arbitrasi/Hakim_HI", description="Jumlah kasus diselesaikan per mekanisme.")
    sisa_kasus: int | None = Field(default=None, alias="Sisa_Kasus", description="Kasus belum terselesaikan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}

