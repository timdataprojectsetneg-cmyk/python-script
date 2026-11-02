"""Pydantic schema — Kemnaker Lapor PKB di WLKP Table 2 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    provinsi: str | None = Field(default=None, alias="Provinsi", description="Nama provinsi (\"Jumlah\" = nasional).")
    a: int | None = Field(default=None, alias="A", description="Perusahaan yang melaporkan PKB lapangan usaha kategori A – Pertanian, Kehutanan dan Perikanan.")
    b: int | None = Field(default=None, alias="B", description="Perusahaan yang melaporkan PKB lapangan usaha kategori B – Pertambangan dan Penggalian.")
    c: int | None = Field(default=None, alias="C", description="Perusahaan yang melaporkan PKB lapangan usaha kategori C – Industri Pengolahan.")
    d: int | None = Field(default=None, alias="D", description="Perusahaan yang melaporkan PKB lapangan usaha kategori D – Pengadaan Listrik dan Gas.")
    e: int | None = Field(default=None, alias="E", description="Perusahaan yang melaporkan PKB lapangan usaha kategori E – Pengadaan Air, Pengelolaan Sampah, Limbah, dan Daur Ulang.")
    f: int | None = Field(default=None, alias="F", description="Perusahaan yang melaporkan PKB lapangan usaha kategori F – Konstruksi.")
    g: int | None = Field(default=None, alias="G", description="Perusahaan yang melaporkan PKB lapangan usaha kategori G – Perdagangan Besar dan Eceran; Reparasi dan Perawatan Mobil dan Sepeda Motor.")
    h: int | None = Field(default=None, alias="H", description="Perusahaan yang melaporkan PKB lapangan usaha kategori H – Transportasi dan Pergudangan.")
    i: int | None = Field(default=None, alias="I", description="Perusahaan yang melaporkan PKB lapangan usaha kategori I – Penyediaan Akomodasi dan Makan Minum.")
    j: int | None = Field(default=None, alias="J", description="Perusahaan yang melaporkan PKB lapangan usaha kategori J – Informasi dan Komunikasi.")
    k: int | None = Field(default=None, alias="K", description="Perusahaan yang melaporkan PKB lapangan usaha kategori K – Jasa Keuangan dan Asuransi.")
    l: int | None = Field(default=None, alias="L", description="Perusahaan yang melaporkan PKB lapangan usaha kategori L – Real Estat.")
    m_n: int | None = Field(default=None, alias="M_N", description="Perusahaan yang melaporkan PKB lapangan usaha kategori M,N – Jasa Perusahaan.")
    o: int | None = Field(default=None, alias="O", description="Perusahaan yang melaporkan PKB lapangan usaha kategori O – Administrasi Pemerintahan, Pertahanan dan Jaminan Sosial Wajib.")
    p: int | None = Field(default=None, alias="P", description="Perusahaan yang melaporkan PKB lapangan usaha kategori P – Jasa Pendidikan.")
    q: int | None = Field(default=None, alias="Q", description="Perusahaan yang melaporkan PKB lapangan usaha kategori Q – Jasa Kesehatan dan Kegiatan Sosial.")
    r_s_t_u: int | None = Field(default=None, alias="R_S_T_U", description="Perusahaan yang melaporkan PKB lapangan usaha kategori R,S,T,U – Jasa Lainnya.")
    tidak_teridentifikasi: int | None = Field(default=None, alias="Tidak_Teridentifikasi", description="Perusahaan yang melaporkan PKB yang lapangan usahanya belum teridentifikasi.")
    tahun: str | None = Field(default=None, alias="tahun", description="Tahun Pelaporan")
    bulan: str | None = Field(default=None, alias="bulan", description="Bulan Pelaporan")
    jumlah: int | None = Field(default=None, alias="Jumlah", description="Total seluruh lapangan usaha.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
