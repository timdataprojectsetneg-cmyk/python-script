"""Pydantic schema — Pola Layanan BBM, LPG, Aviasi, dan Petrokimia (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field, field_validator


class Record(BaseModel):
    jalur_id: str | None = Field(default=None, alias="Jalur ID", description="Kode identifikasi yang diberikan saat penyusunan hasil ekstraksi, misalnya J01 sampai J06, untuk membedakan baris pola layanan. Kode ini bukan nomor jalur resmi dalam laporan dan tidak menunjukkan lokasi geografis, kapasitas, atau nomor fasilitas.")
    kelompok_produk: str | None = Field(default=None, alias="Kelompok Produk", description="Kelompok layanan yang diringkas dari diagram: BBM Ritel, BBM Industri, Aviasi, LPG, atau Petrokimia. LPG dibedakan menjadi beberapa baris berdasarkan kelompok pelanggan; kategori ini bukan daftar produk komersial individual.")
    sumber_produk: str | None = Field(default=None, alias="Sumber Produk", description="Asal penyediaan produk menurut diagram layanan, yaitu Kilang dan/atau Impor. JSON menyimpan beberapa asal sebagai array teks; model ingestion mengubahnya menjadi teks dengan pemisah titik koma. Daftar asal tidak menyatakan proporsi pasokan atau memastikan setiap fasilitas menerima pasokan dari semua asal.")
    storage: str | None = Field(default=None, alias="Storage", description="Jenis fasilitas penyimpanan dalam diagram layanan: TBBM (terminal bahan bakar minyak), Aviation Fuel Terminal, TLPG (terminal LPG), atau Petchem Storage (penyimpanan petrokimia). Nilai menunjukkan tipe fasilitas, bukan nama lokasi, jumlah aset, atau kapasitas penyimpanan.")
    distributor_rantai: str | None = Field(default=None, alias="Distributor Rantai", description="Lembaga penyalur antara storage dan pelanggan sebagaimana ditabulasi dari diagram, misalnya SPBU, SPBU-LN, Pertashop, agen, SPBE, atau outlet LPG. JSON menyimpan array teks dan ingestion merangkainya dengan titik koma. Beberapa lembaga dapat merupakan alternatif penyalur, bukan urutan wajib; array kosong pada Aviasi berarti tidak ada distributor perantara yang dicatat.")
    pelanggan: str | None = Field(default=None, alias="Pelanggan", description="Kelompok pengguna akhir dalam diagram layanan, seperti transportasi darat/air, industri dan institusi, maskapai, rumah tangga, usaha mikro, nelayan kecil, petani, HOREKA, serta pelanggan domestik/ekspor. Nilai bukan nama pelanggan individual atau jumlah pelanggan.")
    keterangan: str | None = Field(default=None, alias="Keterangan", description="Catatan naratif penyusun yang menjelaskan ringkasan pola layanan dan kelompok pelanggan pada baris terkait. Digunakan sebagai konteks interpretasi diagram, bukan bukti tambahan mengenai rute geografis, volume penjualan, atau jumlah fasilitas.")

    @field_validator("sumber_produk", "distributor_rantai", mode="before")
    @classmethod
    def serialize_text_list(cls, value):
        """Preserve list order in raw text without inferring route edges."""
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return "; ".join(value)
        return value

    model_config = {"populate_by_name": True, "extra": "ignore"}
