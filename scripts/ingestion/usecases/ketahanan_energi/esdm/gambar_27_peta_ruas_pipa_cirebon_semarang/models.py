"""Pydantic schema — Gambar 27 Peta Ruas Pipa Cirebon–Semarang (mirrors the Data Dictionary)."""

from datetime import date
from pydantic import BaseModel, Field


class Record(BaseModel):

    nama_ruas: str | None = Field(default=None, alias="nama_ruas", description="Nama ruas pipa pada header peta: Cirebon–Kandang Haur Timur, Pemalang–Cirebon, Batang–Pemalang")
    panjang_ruas: str | None = Field(default=None, alias="panjang_ruas", description="Panjang perkiraan ruas, tertulis dengan tanda ± di peta")
    row_jenis: str | None = Field(default=None, alias="row_jenis", description="Jenis jalur hak lintas (ROW) yang dilalui: Jalan Tol, Jalan Nasional, atau Pertagas. Satu ruas bisa punya lebih dari satu jenis")
    row_keterangan: str | None = Field(default=None, alias="row_keterangan", description="Rincian ROW: titik awal–akhir (mis. gate tol) atau badan usaha jalan tol (BUJT) yang terlibat")
    fasilitas_pendukung: str | None = Field(default=None, alias="fasilitas_pendukung", description="Fasilitas yang disebut pada ruas tersebut, mis. kompresor. Kosong bila tidak ada")
    periode_data: str | None = Field(default=None, alias="periode_data", description="Posisi tanggal pelaporan progres, mis. \"Hingga Desember 2024\" atau \"24 Desember 2025\"")
    progres_realisasi: str | None = Field(default=None, alias="progres_realisasi", description="Progres fisik terealisasi pada periode tersebut")
    progres_rencana: str | None = Field(default=None, alias="progres_rencana", description="Progres fisik rencana (s-curve) pada periode yang sama")
    deviasi: str | None = Field(default=None, alias="deviasi", description="Kolom turunan (formula): realisasi − rencana. Positif berarti di atas rencana")
    keterangan_status: str | None = Field(default=None, alias="keterangan_status", description="Status pekerjaan yang tertulis pada teks, mis. penanaman pipa selesai dan masuk tahap precommissioning")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
