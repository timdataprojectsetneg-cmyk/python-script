"""Pydantic schema — Satu Data Kemnaker.

The Data Dictionary maps a few canonical names onto this API's columns:

===================  =========================================
Data Dictionary      API field / mapping
===================  =========================================
``link_file``        ``file`` (download URL)
``abstraksi``        ``abstraksi`` (HTML string, not Integer)
``kategori``         ``ketenagakerjaan.nama`` (nested object)
``is_deleted``       ``is_deleted`` (0/1 -> bool)
===================  =========================================
"""

from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class SatuDataKemnakerRecord(BaseModel):
    id: int | None = Field(default=None)
    judul: str | None = Field(default=None)
    link_file: str | None = Field(
        default=None, validation_alias=AliasChoices("link_file", "file")
    )
    abstraksi: str | None = Field(default=None)
    isi: str | None = Field(default=None)
    size_files: str | None = Field(default=None)
    kategori: str | None = Field(default=None)
    total_download: int | None = Field(default=None)
    is_deleted: bool | None = Field(default=None)
    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)
    deleted_at: str | None = Field(default=None)

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        data = dict(data)
        kategori = data.get("ketenagakerjaan")
        if isinstance(kategori, dict):
            data["kategori"] = kategori.get("nama")
        if data.get("is_deleted") in (0, 1):
            data["is_deleted"] = bool(data["is_deleted"])
        return data


Record = SatuDataKemnakerRecord
