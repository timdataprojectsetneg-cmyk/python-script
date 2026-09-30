"""Pydantic schema — Satu Data Kemnaker (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    judul: str | None = Field(default=None, alias="judul")
    link_file: int | None = Field(default=None, alias="link_file")
    abstraksi: int | None = Field(default=None, alias="abstraksi")
    created_at: str | None = Field(default=None, alias="created_at")
    updated_at: str | None = Field(default=None, alias="updated_at")
    is_deleted: bool | None = Field(default=None, alias="is_deleted")
    deleted_at: str | None = Field(default=None, alias="deleted_at")

    model_config = {"populate_by_name": True, "extra": "ignore"}

