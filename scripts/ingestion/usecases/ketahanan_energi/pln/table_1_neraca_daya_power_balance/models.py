"""Pydantic schema — Table 1 : Neraca Daya / Power Balance (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    unit_pln: str | None = Field(default=None, alias="Unit_PLN", description="Nama unit PLN, sub-unit provinsi (baris berawalan \"-\" di tabel sumber), atau baris agregat (Luar Jawa, Jawa, Indonesia)")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"unit\", \"sub_unit\" (provinsi di bawah unit induk, bertanda \"-\" di sumber), \"subtotal_wilayah\" (Luar Jawa atau Jawa), \"proyek\", atau \"total\"")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2025)")
    unit_pln: str | None = Field(default=None, alias="unit_pln", description="Nama unit PLN (UID, UIW, UIP3B, UIK, PLN Indonesia Power, PLN Nusantara Power, dll.), baris agregat \"Luar Jawa\" dan \"Jawa\", \"Proyek Pembangkitan\", atau \"Indonesia\"")

    induk_unit: str | None = Field(default=None, alias="induk_unit", description="Nama unit induk untuk baris \"sub_unit\" (misalnya \"UID Riau dan Kepulauan Riau\" untuk Riau). Bernilai null untuk baris lain")
    kelompok_wilayah: str | None = Field(default=None, alias="kelompok_wilayah", description="Kelompok wilayah baris tersebut: \"Luar Jawa\" atau \"Jawa\". Bernilai null untuk baris proyek dan total")
    kapasitas_terpasang_mw: float | None = Field(default=None, alias="kapasitas_terpasang_mw", description="Kapasitas terpasang pembangkit milik PLN, sewa, dan IPP. Bernilai null jika di tabel tertulis \"-\"")
    daya_mampu_mw: float | None = Field(default=None, alias="daya_mampu_mw", description="Daya mampu pembangkit milik PLN, sewa, dan IPP. Bernilai null jika di tabel tertulis \"-\"")
    beban_puncak_mw: float | None = Field(default=None, alias="beban_puncak_mw", description="Beban puncak. Bernilai null jika di tabel tertulis \"-\"")
    model_config = {"populate_by_name": True, "extra": "ignore"}
