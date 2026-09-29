"""Pydantic schema — Data Mogok Kerja.

Source columns are mapped to canonical fields with Pydantic validation aliases:

===================  ==============================
Source / extractor   Field
===================  ==============================
``Provinsi``         ``wilayah``
``Jumlah_Kasus``     ``kasus``
``Jumlah_Pekerja``   ``tenaga_kerja_yang_terlibat``
``Tahun``            ``tahun`` (derived from ``Periode`` when absent)
===================  ==============================
"""

from __future__ import annotations

import re

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class DataMogokKerjaRecord(BaseModel):
    wilayah: str | None = Field(
        default=None, validation_alias=AliasChoices("Provinsi", "wilayah", "provinsi")
    )
    kasus: int = Field(
        default=0, ge=0, validation_alias=AliasChoices("Jumlah_Kasus", "Kasus", "jumlah_kasus", "kasus")
    )
    tenaga_kerja_yang_terlibat: int = Field(
        default=0,
        ge=0,
        validation_alias=AliasChoices(
            "Jumlah_Pekerja", "Tenaga Kerja yang Terlibat", "jumlah_pekerja", "tenaga_kerja_yang_terlibat"
        ),
    )
    tahun: str | None = Field(default=None, validation_alias=AliasChoices("Tahun", "tahun"))

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _derive_tahun(cls, data: object) -> object:
        """Use ``Periode`` (e.g. "Januari s.d Maret 2026") to fill ``tahun`` ("2026")."""
        if isinstance(data, dict) and not (data.get("Tahun") or data.get("tahun")):
            source = data.get("Periode") or data.get("periode")
            match = re.search(r"(20\d{2})", str(source or ""))
            if match:
                data = {**data, "Tahun": match.group(1)}
        return data


# Registry looks up ``models.Record``.
Record = DataMogokKerjaRecord
