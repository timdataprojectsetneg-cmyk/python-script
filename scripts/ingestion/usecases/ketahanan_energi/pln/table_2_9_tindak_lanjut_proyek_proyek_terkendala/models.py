"""Pydantic schema — Table 2.9 : Tindak Lanjut Proyek-Proyek Terkendala (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    pembangkit: str | None = Field(default=None, alias="pembangkit", description="Nama pembangkit terkendala")
    kapasitas: str | None = Field(default=None, alias="kapasitas", description="Kapasitas dalam format jumlah unit x MW per unit (misalnya \"2x7\"), atau MW tunggal (misalnya \"30\")")
    pengembang: str | None = Field(default=None, alias="pengembang", description="Pengembang proyek: PLN atau IPP")
    rencana_cod: str | None = Field(default=None, alias="rencana_cod", description="Rencana COD: \"Operasi\" untuk yang sudah beroperasi, tahun (misalnya \"2033\"), atau keterangan bertahap (misalnya \"2025 (14 MW)/2026 (14 MW)\")")

    no: int | None = Field(default=None, alias="no", description="Nomor urut proyek")
    status_proyek: str | None = Field(default=None, alias="status_proyek", description="Kelompok proyek di sumber: \"Selesai\" (no 1-17) atau \"Dilanjutkan\" (no 18-34)")
    keterangan_dilanjutkan: str | None = Field(default=None, alias="keterangan_dilanjutkan", description="Bernilai \"Dilanjutkan\" jika proyek dilanjutkan. Null jika kosong di sumber")
    keterangan_diganti: str | None = Field(default=None, alias="keterangan_diganti", description="Bentuk penggantian proyek (GI, PLTMG, PLTD, MPP, \"Relokasi MPP\", \"Relokasi Sorong***\", dll.). Null jika kosong di sumber")
    model_config = {"populate_by_name": True, "extra": "ignore"}
