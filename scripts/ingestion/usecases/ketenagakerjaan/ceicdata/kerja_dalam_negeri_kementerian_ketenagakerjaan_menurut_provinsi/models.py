"""Pydantic schema — Tabel ID.GBA: Penempatan Kerja: Dalam Negeri: Kementerian Ketenagakerjaan: Menurut Provinsi (mirrors the Data Dictionary)."""
from pydantic import ConfigDict
from datetime import date as DateType

from pydantic import BaseModel, Field


class Record(BaseModel):

    model_config = {"populate_by_name": True, "extra": "ignore"}
