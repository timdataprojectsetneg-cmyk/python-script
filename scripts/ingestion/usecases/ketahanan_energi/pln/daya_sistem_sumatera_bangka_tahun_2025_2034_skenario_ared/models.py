"""Pydantic schema — Tabel 5.83 Neraca Daya Sistem Sumatera-Bangka Tahun 2025-2034 Skenario ARED (mirrors the Data Dictionary)."""

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    """TODO: fill fields from docs/<usecase>/dictionary_<source>.md."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
