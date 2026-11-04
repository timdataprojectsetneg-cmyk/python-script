"""Pydantic schema — Tabel Kinerja SAIDI dan SAIFI (mirrors the Data Dictionary)."""
from pydantic import Field

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    """TODO: fill fields from docs/<usecase>/dictionary_<source>.md."""

    keterangan: str | None = Field(default=None, alias="keterangan", description="Indikator kinerja keandalan listrik: \"Rerata Durasi Gangguan Per Pelanggan (SAIDI)\" atau \"Rerata Frekuensi Gangguan Per Pelanggan (SAIFI)\"")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai pada indikator tersebut: \"Menit/Pelanggan\" (SAIDI) atau \"Kali/Pelanggan\" (SAIFI)")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2023, 2024, 2025)")
    nilai: float | None = Field(default=None, alias="nilai", description="Nilai SAIDI atau SAIFI pada tahun terkait, dalam format desimal standar (titik)")
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
