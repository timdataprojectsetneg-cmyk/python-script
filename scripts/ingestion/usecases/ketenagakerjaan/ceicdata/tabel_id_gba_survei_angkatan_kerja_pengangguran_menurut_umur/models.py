"""Pydantic schema — Tabel ID.GBA: Survei Angkatan Kerja: Pengangguran: Menurut Umur (mirrors the Data Dictionary)."""
from datetime import date as DateType

from pydantic import BaseModel, Field


class Record(BaseModel):

    table_id: str | None = Field(default=None, alias="table_id", description="Kode tabel CEIC (TBxxxx) sumber data")
    series_id: int | None = Field(default=None, alias="series_id", description="ID series CEIC")
    series_name: str | None = Field(default=None, alias="series_name", description="Nama lengkap series; memuat dimensi seperti provinsi, usia, atau industri")
    unit: str | None = Field(default=None, alias="unit", description="Satuan nilai dari metadata CEIC (mis. Person th)")
    frequency: str | None = Field(default=None, alias="frequency", description="Frekuensi data (mis. Semiannually, Annual, Monthly)")
    province: str | None = Field(default=None, alias="province", description="Provinsi dari metadata series; null bila series nasional")
    date: DateType | None = Field(default=None, alias="date", description="Periode observasi (YYYY-MM-DD)")
    value: float | None = Field(default=None, alias="value", description="Nilai observasi")
    last_update_time: DateType | None = Field(default=None, alias="last_update_time", description="Tanggal terakhir data diperbarui di CEIC (YYYY-MM-DD)")
    model_config = {"populate_by_name": True, "extra": "ignore"}
