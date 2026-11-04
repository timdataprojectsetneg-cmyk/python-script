"""Pydantic schema — Infografis Capaian Kinerja 2025 (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    nilai: float | None = Field(default=None, alias="nilai", description="Nilai angka indikator (pemisah desimal titik; pemisah ribuan dihilangkan)")

    label: str | None = Field(default=None, alias="Label", description="Deskripsi")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data. Capaian kinerja 2025; khusus realisasi anggaran tersedia 2021-2025")
    kelompok: str | None = Field(default=None, alias="kelompok", description="Kelompok indikator sesuai infografis: Realisasi Anggaran, PNBP, Penyaluran JBT dan JBKP, BBM Satu Harga, Infrastruktur Gas Bumi, Pengangkutan dan Niaga Gas Bumi")
    indikator: str | None = Field(default=None, alias="indikator", description="Nama indikator dalam kelompok, mis. Anggaran BPH Migas, JBT Minyak Solar, Pipa Transmisi")
    tipe_nilai: str | None = Field(default=None, alias="tipe_nilai", description="Jenis nilai: Pagu, Target, Realisasi, Realisasi Kumulatif, Persentase, Penetapan Kuota, Penyaluran")
    satuan: str | None = Field(default=None, alias="satuan", description="Satuan nilai: Miliar Rupiah, %, Juta Kilo Liter, Lembaga Penyalur, KM, Miliar MSCF")
    cakupan_wilayah: str | None = Field(default=None, alias="Cakupan Wilayah", description="Cakupan agregasi data, dalam sumber ini nasional")
    periode_verifikasi: str | None = Field(default=None, alias="Periode Verifikasi", description="Periode yang digunakan untuk menghitung realisasi penyaluran")
    sumber: str | None = Field(default=None, alias="Sumber", description="Laporan Kinerja BPH Migas Tahun 2025")
    model_config = {"populate_by_name": True, "extra": "ignore", "coerce_numbers_to_str": True}
