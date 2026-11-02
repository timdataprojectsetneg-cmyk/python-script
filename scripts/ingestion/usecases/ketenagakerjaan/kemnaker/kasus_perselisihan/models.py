"""Pydantic schema — Kasus Perselisihan (mirrors the Data Dictionary).

One row per (month, jenis perselisihan): jumlah perselisihan (pusat/daerah/
jumlah), penyelesaian per mekanisme, sisa kasus. ``periode``/``tahun`` are
derived from the month sheet name and the 'Tahun <yyyy>' title row.
"""

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    periode: str | None = Field(default=None, alias="Periode", description="Periode data, kumulatif sejak Januari (contoh: \"Januari s.d. Juni 2025\").")
    jenis_perselisihan: str | None = Field(
        default=None, alias="Jenis_Perselisihan",
        description="Perselisihan Hak / Kepentingan / PHK / Serikat Pekerja.",
    )
    mediasi_pb: int | None = Field(default=None, alias="Mediasi_PB", description="Diselesaikan mediasi dengan Perjanjian Bersama.")
    mediasi_anjuran: int | None = Field(default=None, alias="Mediasi_Anjuran", description="Diselesaikan mediasi dengan anjuran mediator.")
    hakim_hi: int | None = Field(default=None, alias="Hakim_HI", description="Diselesaikan melalui Pengadilan Hubungan Industrial.")
    sisa_kasus: int | None = Field(default=None, alias="Sisa_Kasus", description="Kasus yang belum selesai.")

    kasus_pusat: int | None = Field(default=None, alias="Kasus_Pusat", description="Perselisihan tercatat di tingkat pusat.")
    kasus_daerah: int | None = Field(default=None, alias="Kasus_Daerah", description="Perselisihan tercatat di tingkat daerah.")
    jumlah_kasus: int | None = Field(default=None, alias="Jumlah_Kasus", description="Jumlah perselisihan yang ditangani mediator.")
    selesai_bipartit: int | None = Field(default=None, alias="Selesai_Bipartit", description="Diselesaikan melalui bipartit.")
    selesai_konsiliasi: int | None = Field(default=None, alias="Selesai_Konsiliasi", description="Diselesaikan melalui konsiliasi.")
    selesai_arbitrase: int | None = Field(default=None, alias="Selesai_Arbitrase", description="Diselesaikan melalui arbitrase.")
    jumlah_selesai: int | None = Field(default=None, alias="Jumlah_Selesai", description="Total kasus yang telah diselesaikan.")
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
