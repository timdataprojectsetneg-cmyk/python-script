"""Pydantic schema for UN Status Traktat Multilateral."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UnStatusTraktatMultilateralRecord(BaseModel):
    id_traktat: str = Field(
        description="Nomor registrasi traktat multilateral UN Treaty Collection (misal: 'UNTC-XXVII-7')."
    )
    nama_konvensi_internasional: str = Field(
        description="Nama konvensi atau protokol internasional."
    )
    organisasi_penyimpan_depository: str = Field(
        default="Sekjen PBB",
        description="Lembaga penyimpan traktat (Sekjen PBB, WIPO, IAEA, dll.)."
    )
    tanggal_adopsi_dunia: Optional[str] = Field(
        default=None,
        description="Waktu traktat diadopsi secara global (format YYYY-MM-DD)."
    )
    status_keikutsertaan_indonesia: str = Field(
        default="Pihak (Diratifikasi)",
        description="Status keikutsertaan (Pihak / Diratifikasi, Penandatangan, Belum Menjadi Pihak)."
    )
    dokumen_pengesahan_uu_ri: Optional[str] = Field(
        default=None,
        description="Nomor UU atau regulasi ratifikasi Indonesia (misal: 'UU No. 16 Tahun 2016')."
    )
    tanggal_penyerahan_instrumen: Optional[str] = Field(
        default=None,
        description="Waktu deposit instrumen ratifikasi ke Sekjen PBB (format YYYY-MM-DD)."
    )
    catatan_reservasi_deklarasi: Optional[str] = Field(
        default=None,
        description="Pernyataan deklarasi interpretatif atau reservasi pasal tertentu oleh RI."
    )
    data_source: str = Field(
        default="United Nations Treaty Collection (UNTC) & Kemenlu RI",
        description="Lembaga penerbit resmi data."
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


# Registry looks up models.Record
Record = UnStatusTraktatMultilateralRecord
