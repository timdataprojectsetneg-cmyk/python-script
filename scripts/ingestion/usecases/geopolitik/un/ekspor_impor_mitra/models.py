"""Pydantic schema mirroring dictionary_ekspor_impor_mitra.md."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EksporImporMitraRecord(BaseModel):
    period: int = Field(description="Tahun perdagangan.")
    reportercode: int = Field(alias="reporterCode", description="Kode negara pelapor. 360 = Indonesia.")
    flowcode: str = Field(alias="flowCode", description="X = ekspor; M = impor.")
    partnercode: int = Field(alias="partnerCode", description="Kode negara mitra dalam hasil API.")
    partner_name: Optional[str] = Field(
        default=None, description="Label mitra dipetakan dari kode UN M49; bukan field terisi API preview."
    )
    cmdcode: str = Field(
        alias="cmdCode",
        description="TOTAL = semua barang; 10 = serealia; 27 = bahan bakar mineral; 72 = besi/baja; 85 = mesin/peralatan listrik.",
    )
    primaryvalue: Optional[float] = Field(
        default=None, alias="primaryValue", description="Nilai utama perdagangan dari API (USD)."
    )
    isreported: Optional[bool] = Field(
        default=None, alias="isReported", description="Flag data dilaporkan langsung, dipertahankan dari sumber."
    )
    isaggregate: Optional[bool] = Field(
        default=None, alias="isAggregate", description="Flag agregasi sumber."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


Record = EksporImporMitraRecord
