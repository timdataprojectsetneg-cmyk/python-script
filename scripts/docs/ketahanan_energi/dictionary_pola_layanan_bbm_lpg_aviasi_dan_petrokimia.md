# Data Dictionary: Pola Layanan BBM, LPG, Aviasi, dan Petrokimia

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Pola Layanan BBM, LPG, Aviasi, dan Petrokimia`
- Publisher: pertamina
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Pertamina_Pola Layanan](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=JtsOIf&nav=MTVfezlFODQ1QTM4LUY1OEItNEYxOS1BNTUwLTRBOEM4RDREMEY4RX0)
- Target module: `ingestion/usecases/ketahanan_energi/pertamina/pola_layanan_bbm_lpg_aviasi_dan_petrokimia/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Jalur ID | `jalur_id` | Text | - | Kode identifikasi yang diberikan saat penyusunan hasil ekstraksi, misalnya J01 sampai J06, untuk membedakan baris pola layanan. Kode ini bukan nomor jalur resmi dalam laporan dan tidak menunjukkan lokasi geografis, kapasitas, atau nomor fasilitas. |
| Kelompok Produk | `kelompok_produk` | Categorical | - | Kelompok layanan yang diringkas dari diagram: BBM Ritel, BBM Industri, Aviasi, LPG, atau Petrokimia. LPG dibedakan menjadi beberapa baris berdasarkan kelompok pelanggan; kategori ini bukan daftar produk komersial individual. |
| Sumber Produk | `sumber_produk` | Text | - | Asal penyediaan produk menurut diagram layanan, yaitu Kilang dan/atau Impor. JSON menyimpan beberapa asal sebagai array teks; model ingestion mengubahnya menjadi teks dengan pemisah titik koma. Daftar asal tidak menyatakan proporsi pasokan atau memastikan setiap fasilitas menerima pasokan dari semua asal. |
| Storage | `storage` | Text | - | Jenis fasilitas penyimpanan dalam diagram layanan: TBBM (terminal bahan bakar minyak), Aviation Fuel Terminal, TLPG (terminal LPG), atau Petchem Storage (penyimpanan petrokimia). Nilai menunjukkan tipe fasilitas, bukan nama lokasi, jumlah aset, atau kapasitas penyimpanan. |
| Distributor Rantai | `distributor_rantai` | Text | - | Lembaga penyalur antara storage dan pelanggan sebagaimana ditabulasi dari diagram, misalnya SPBU, SPBU-LN, Pertashop, agen, SPBE, atau outlet LPG. JSON menyimpan array teks dan ingestion merangkainya dengan titik koma. Beberapa lembaga dapat merupakan alternatif penyalur, bukan urutan wajib; array kosong pada Aviasi berarti tidak ada distributor perantara yang dicatat. |
| Pelanggan | `pelanggan` | Text | - | Kelompok pengguna akhir dalam diagram layanan, seperti transportasi darat/air, industri dan institusi, maskapai, rumah tangga, usaha mikro, nelayan kecil, petani, HOREKA, serta pelanggan domestik/ekspor. Nilai bukan nama pelanggan individual atau jumlah pelanggan. |
| Keterangan | `keterangan` | Text | - | Catatan naratif penyusun yang menjelaskan ringkasan pola layanan dan kelompok pelanggan pada baris terkait. Digunakan sebagai konteks interpretasi diagram, bukan bukti tambahan mengenai rute geografis, volume penjualan, atau jumlah fasilitas. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class PolaLayananBbmLpgAviasiDanPetrokimiaRecord(BaseModel):
    jalur_id: str | None = Field(default=None, alias="Jalur ID", description="Kode identifikasi yang diberikan saat penyusunan hasil ekstraksi, misalnya J01 sampai J06, untuk membedakan baris pola layanan. Kode ini bukan nomor jalur resmi dalam laporan dan tidak menunjukkan lokasi geografis, kapasitas, atau nomor fasilitas.")
    kelompok_produk: str | None = Field(default=None, alias="Kelompok Produk", description="Kelompok layanan yang diringkas dari diagram: BBM Ritel, BBM Industri, Aviasi, LPG, atau Petrokimia. LPG dibedakan menjadi beberapa baris berdasarkan kelompok pelanggan; kategori ini bukan daftar produk komersial individual.")
    sumber_produk: str | None = Field(default=None, alias="Sumber Produk", description="Asal penyediaan produk menurut diagram layanan, yaitu Kilang dan/atau Impor. JSON menyimpan beberapa asal sebagai array teks; model ingestion mengubahnya menjadi teks dengan pemisah titik koma. Daftar asal tidak menyatakan proporsi pasokan atau memastikan setiap fasilitas menerima pasokan dari semua asal.")
    storage: str | None = Field(default=None, alias="Storage", description="Jenis fasilitas penyimpanan dalam diagram layanan: TBBM (terminal bahan bakar minyak), Aviation Fuel Terminal, TLPG (terminal LPG), atau Petchem Storage (penyimpanan petrokimia). Nilai menunjukkan tipe fasilitas, bukan nama lokasi, jumlah aset, atau kapasitas penyimpanan.")
    distributor_rantai: str | None = Field(default=None, alias="Distributor Rantai", description="Lembaga penyalur antara storage dan pelanggan sebagaimana ditabulasi dari diagram, misalnya SPBU, SPBU-LN, Pertashop, agen, SPBE, atau outlet LPG. JSON menyimpan array teks dan ingestion merangkainya dengan titik koma. Beberapa lembaga dapat merupakan alternatif penyalur, bukan urutan wajib; array kosong pada Aviasi berarti tidak ada distributor perantara yang dicatat.")
    pelanggan: str | None = Field(default=None, alias="Pelanggan", description="Kelompok pengguna akhir dalam diagram layanan, seperti transportasi darat/air, industri dan institusi, maskapai, rumah tangga, usaha mikro, nelayan kecil, petani, HOREKA, serta pelanggan domestik/ekspor. Nilai bukan nama pelanggan individual atau jumlah pelanggan.")
    keterangan: str | None = Field(default=None, alias="Keterangan", description="Catatan naratif penyusun yang menjelaskan ringkasan pola layanan dan kelompok pelanggan pada baris terkait. Digunakan sebagai konteks interpretasi diagram, bukan bukti tambahan mengenai rute geografis, volume penjualan, atau jumlah fasilitas.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
