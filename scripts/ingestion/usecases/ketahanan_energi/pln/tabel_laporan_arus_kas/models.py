"""Pydantic schema — Tabel Laporan arus kas (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    periode: int | None = Field(default=None, alias="Periode", description="Tahun buku")
    aktivitas: str | None = Field(default=None, alias="Aktivitas", description="Operasi atau Investasi")
    komponen_arus_kas: str | None = Field(default=None, alias="Komponen Arus Kas", description="Pos pada laporan arus kas metode langsung")
    jenis: str | None = Field(default=None, alias="Jenis", description="Capex, Penerimaan, atau Total")
    nilai: str | None = Field(default=None, alias="Nilai", description="Bertanda kurung = kas keluar")
    rasio: str | None = Field(default=None, alias="Rasio", description="Rumus: capex / depresiasi (sheet COGS)")

    model_config = {"populate_by_name": True, "extra": "ignore"}
