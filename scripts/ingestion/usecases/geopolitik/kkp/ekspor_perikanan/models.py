"""Pydantic schema mirroring the Data Dictionary for Ekspor Perikanan KKP."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EksporPerikananRecord(BaseModel):
    # extra="allow": the portal adds a new year column every year; keep it instead of dropping it.
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    komoditas: str = Field(
        alias="Komoditas", description="Kelompok komoditas hasil perikanan pada tabel KKP."
    )
    nilai_2019: Optional[float] = Field(default=None, alias="2019", description="Nilai ekspor 2019 (Ribu USD).")
    nilai_2020: Optional[float] = Field(default=None, alias="2020", description="Nilai ekspor 2020 (Ribu USD).")
    nilai_2021: Optional[float] = Field(default=None, alias="2021", description="Nilai ekspor 2021 (Ribu USD).")
    nilai_2022: Optional[float] = Field(default=None, alias="2022", description="Nilai ekspor 2022 (Ribu USD).")
    nilai_2023: Optional[float] = Field(default=None, alias="2023", description="Nilai ekspor 2023 (Ribu USD).")
    nilai_2024: Optional[float] = Field(default=None, alias="2024", description="Nilai ekspor 2024 (Ribu USD).")
    nilai_2025: Optional[float] = Field(default=None, alias="2025", description="Nilai ekspor 2025 (Ribu USD).")
    nilai_2026: Optional[float] = Field(
        default=None, alias="2026", description="Nilai ekspor 2026 (Ribu USD); tahun berjalan, parsial."
    )


Record = EksporPerikananRecord
