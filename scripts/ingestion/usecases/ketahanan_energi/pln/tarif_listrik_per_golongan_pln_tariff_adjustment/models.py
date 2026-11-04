"""Pydantic schema — Tarif Listrik per Golongan - PLN Tariff Adjustment (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    periode_berlaku: str | None = Field(default=None, alias="Periode Berlaku", description="Periode tarif yang berlaku.")
    golongan_pelanggan: str | None = Field(default=None, alias="Golongan Pelanggan", description="Kode golongan tarif pelanggan PLN.")
    daya: str | None = Field(default=None, alias="Daya", description="Rentang daya yang termasuk dalam golongan.")
    tegangan: str | None = Field(default=None, alias="Tegangan", description="Tingkat tegangan pelayanan.")
    tarif_listrik: float | None = Field(default=None, alias="Tarif Listrik", description="Tarif tenaga listrik untuk golongan pelanggan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
