"""Pydantic schema — Gambar 29 Peta Pipa Transmisi Gas Bumi Ruas Dumai Sei Mangkei Medan (mirrors the Data Dictionary)."""

from datetime import date
from pydantic import BaseModel, Field


class Record(BaseModel):
    nama_pipa: str | None = Field(default=None, alias="nama_pipa", description="Nama pipa transmisi pada judul slide: Pipa Transmisi Gas Bumi Dumai–Sei Mangkei–Medan (DUSEM)")

    titik_rute: str | None = Field(default=None, alias="titik_rute", description="Lokasi yang diberi label pada peta di sepanjang rute pipa")
    panjang_pipa: str | None = Field(default=None, alias="panjang_pipa", description="Panjang perkiraan pipa, tertulis dengan tanda ± pada kotak keterangan peta")
    sumber_pasokan: str | None = Field(default=None, alias="sumber_pasokan", description="Sumber gas yang akan dialirkan menurut teks slide")
    peruntukan: str | None = Field(default=None, alias="peruntukan", description="Kebutuhan yang dilayani menurut teks slide")
    manfaat: str | None = Field(default=None, alias="manfaat", description="Manfaat pembangunan pipa yang dicantumkan slide (poin a–d)")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
