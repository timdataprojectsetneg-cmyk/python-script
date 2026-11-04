"""Pydantic schema — DATA LEMBAGA PENYALUR BBM MELALUI STASIUN PENGISIAN - (KBLI 47301) (mirrors the Data Dictionary)."""
from pydantic import Field

from pydantic import BaseModel, ConfigDict


class Record(BaseModel):
    """TODO: fill fields from docs/<usecase>/dictionary_<source>.md."""

    no: int | None = Field(default=None, alias="No", description="Nomor urut baris tabel")
    no_spbu: str | None = Field(default=None, alias="No SPBU", description="Nomor SPBU/penyalur, mis. 4854304 atau 4P57611")
    nama_penyalur: str | None = Field(default=None, alias="Nama Penyalur", description="Nama badan usaha penyalur BBM")
    bentuk_penyalur: str | None = Field(default=None, alias="Bentuk Penyalur", description="SPBU, SPBUN, Pertashop, AMT, atau SPBB (Agen BBM/SPBU/SPBN/SPB Bunker/Lainnya)")
    alamat_spbu: str | None = Field(default=None, alias="Alamat SPBU", description="Alamat stasiun pengisian sebagaimana tertulis di laporan")
    kota_kabupaten: str | None = Field(default=None, alias="Kota/Kabupaten", description="Kota/kabupaten lokasi SPBU, mis. Kab Kebumen")
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Provinsi lokasi SPBU")
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
