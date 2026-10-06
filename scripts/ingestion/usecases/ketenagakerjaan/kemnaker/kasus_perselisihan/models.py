"""Pydantic schema — Kasus Perselisihan (mirrors the Data Dictionary).

One row per (month, jenis perselisihan): jumlah perselisihan (pusat/daerah/
jumlah), penyelesaian per mekanisme, sisa kasus. ``periode``/``tahun`` are
derived from the month sheet name and the 'Tahun <yyyy>' title row.
"""

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Periode bulan, format YYYY-MM.")
    tahun: int | None = Field(default=None, alias="Tahun", description="Tahun data.")
    jenis_perselisihan: str | None = Field(
        default=None, alias="Jenis_Perselisihan",
        description="Perselisihan Hak / Kepentingan / PHK / Serikat Pekerja.",
    )
    jumlah_pusat: int | None = Field(default=None, alias="Jumlah_Pusat", description="Jumlah perselisihan di tingkat pusat.")
    jumlah_daerah: int | None = Field(default=None, alias="Jumlah_Daerah", description="Jumlah perselisihan di tingkat daerah.")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total jumlah perselisihan (pusat + daerah).")
    bipartit: int | None = Field(default=None, alias="Bipartit", description="Diselesaikan melalui Bipartit.")
    mediasi_pb: int | None = Field(default=None, alias="Mediasi_PB", description="Diselesaikan melalui Mediasi (PB).")
    mediasi_anjuran: int | None = Field(default=None, alias="Mediasi_Anjuran", description="Diselesaikan melalui Mediasi (Anjuran).")
    konsiliasi: int | None = Field(default=None, alias="Konsiliasi", description="Diselesaikan melalui Konsiliasi.")
    arbitrasi: int | None = Field(default=None, alias="Arbitrasi", description="Diselesaikan melalui Arbitrasi.")
    hakim_hi: int | None = Field(default=None, alias="Hakim_HI", description="Diselesaikan melalui Hakim Hubungan Industrial.")
    jumlah_penyelesaian: int | None = Field(default=None, alias="Jumlah_Penyelesaian", description="Total perselisihan yang diselesaikan.")
    sisa_kasus: int | None = Field(default=None, alias="Sisa_Kasus", description="Kasus yang belum terselesaikan.")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
