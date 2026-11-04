# Data Dictionary: Pertamina Patra Niaga Sustainability Report 2025_Wilayah Operasi dan Jaringan Usaha

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `ketahanan_energi`
- Source: `Pertamina Patra Niaga Sustainability Report 2025_Wilayah Operasi dan Jaringan Usaha`
- Publisher: pertamina
- Data access: `Manual`
- Update frequency: Yearly
- Eligible: `True`
- Data Dictionary file: [Pertamina_Wilayah Operasi](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketahanan%20Energi/Pasokan,%20Stok,%20dan%20Distribusi%20Bahan%20Bakar%20dan%20Gas.xlsx?d=we099b80b8f6b4de780d6d9a7bd86fa8b&csf=1&web=1&e=a6JfA3&nav=MTVfezRCNjRGOTQ4LTkwODItNDY4Ni1BQzdCLTZGNDY1OEE5NEIyNX0)
- Target module: `ingestion/usecases/ketahanan_energi/pertamina/niaga_sustainability_report_2025_wilayah_operasi_dan_jaringan/models.py`

## Fields

| Label | Name (column) | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|---|
| Jenis Data | `jenis_data` | Categorical | - | Pembeda kelompok record: Wilayah Operasi, Infrastruktur, atau Rute Pasokan. Setiap kelompok memiliki atribut yang relevan berbeda; kolom yang tidak berlaku bernilai null. Rute Pasokan pada file saat ini berupa ringkasan regional, bukan daftar hubungan asal-tujuan yang terverifikasi. |
| Nomor Regional | `nomor_regional` | Integer | - | Nomor regional operasional dan pemasaran 1–8 sesuai peta: Sumatra Bagian Utara, Sumatra Bagian Selatan, Jawa Bagian Barat, Jawa Bagian Tengah, Jawa Timur/Bali/Nusa Tenggara, Kalimantan, Sulawesi, dan Papua Maluku. Null pada infrastruktur nasional karena aset tidak dirinci per regional. |
| Nama Objek | `nama_objek` | Text | - | Nama regional untuk record Wilayah Operasi; jenis aset untuk record Infrastruktur; atau nama ringkasan jaringan regional untuk record Rute Pasokan. Penafsirannya harus menggunakan Jenis Data, karena kolom ini tidak selalu menyatakan lokasi fasilitas individual. |
| Kantor Regional | `kantor_regional` | Text | - | Kota pusat kantor operasional dan pemasaran regional menurut laporan: Medan, Palembang, Jakarta Pusat, Semarang, Surabaya, Balikpapan, Makassar, atau Jayapura. Diisi pada record regional dan ringkasan jaringannya; null pada infrastruktur nasional. Kota kantor bukan batas cakupan wilayah maupun lokasi seluruh aset. |
| Jumlah | `jumlah` | Numeric | Unit | Jumlah aset atau lokasi infrastruktur secara nasional menurut diagram: Mobil Tangki BBM 4.918, Terminal BBM 121, Terminal Bahan Bakar Penerbangan 72, Terminal LPG 33, FT(S) LPG 17, dan Lokasi STS 3. Bukan jumlah per regional atau kapasitas. Null pada record non-infrastruktur berarti tidak berlaku, bukan nol. |
| Jenis Pasokan | `jenis_pasokan` | Categorical | - | Kategori legenda peta: Impor, Dari Kilang, atau Dari Fuel Terminal. Pada file saat ini ketiganya digabung sebagai teks ringkasan untuk setiap regional; ini belum membuktikan bahwa semua jenis pasokan tersedia pada setiap regional. Jangan gunakan ringkasan tersebut sebagai hubungan rute yang terverifikasi. |
| Node Asal | `node_asal` | Text | - | Lokasi awal suatu hubungan pasokan apabila dapat ditetapkan dari arah garis peta. Saat ini seluruh nilai null karena pasangan asal-tujuan belum berhasil diverifikasi; null tidak berarti tidak ada pasokan. Kolom ini tidak boleh diisi dari dugaan kedekatan geografis. |
| Node Tujuan | `node_tujuan` | Text | - | Lokasi penerima suatu hubungan pasokan apabila dapat ditetapkan dari arah garis peta. Saat ini seluruh nilai null karena pasangan asal-tujuan belum berhasil diverifikasi; record Rute Pasokan hanya ringkasan regional, bukan rute rinci yang dapat dianalisis sebagai jaringan. |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class NiagaSustainabilityReport2025WilayahOperasiDanJaringanRecord(BaseModel):
    jenis_data: str | None = Field(default=None, alias="Jenis Data", description="Pembeda kelompok record: Wilayah Operasi, Infrastruktur, atau Rute Pasokan. Setiap kelompok memiliki atribut yang relevan berbeda; kolom yang tidak berlaku bernilai null. Rute Pasokan pada file saat ini berupa ringkasan regional, bukan daftar hubungan asal-tujuan yang terverifikasi.")
    nomor_regional: int | None = Field(default=None, alias="Nomor Regional", description="Nomor regional operasional dan pemasaran 1–8 sesuai peta: Sumatra Bagian Utara, Sumatra Bagian Selatan, Jawa Bagian Barat, Jawa Bagian Tengah, Jawa Timur/Bali/Nusa Tenggara, Kalimantan, Sulawesi, dan Papua Maluku. Null pada infrastruktur nasional karena aset tidak dirinci per regional.")
    nama_objek: str | None = Field(default=None, alias="Nama Objek", description="Nama regional untuk record Wilayah Operasi; jenis aset untuk record Infrastruktur; atau nama ringkasan jaringan regional untuk record Rute Pasokan. Penafsirannya harus menggunakan Jenis Data, karena kolom ini tidak selalu menyatakan lokasi fasilitas individual.")
    kantor_regional: str | None = Field(default=None, alias="Kantor Regional", description="Kota pusat kantor operasional dan pemasaran regional menurut laporan: Medan, Palembang, Jakarta Pusat, Semarang, Surabaya, Balikpapan, Makassar, atau Jayapura. Diisi pada record regional dan ringkasan jaringannya; null pada infrastruktur nasional. Kota kantor bukan batas cakupan wilayah maupun lokasi seluruh aset.")
    jumlah: str | None = Field(default=None, alias="Jumlah", description="Jumlah aset atau lokasi infrastruktur secara nasional menurut diagram: Mobil Tangki BBM 4.918, Terminal BBM 121, Terminal Bahan Bakar Penerbangan 72, Terminal LPG 33, FT(S) LPG 17, dan Lokasi STS 3. Bukan jumlah per regional atau kapasitas. Null pada record non-infrastruktur berarti tidak berlaku, bukan nol.")
    jenis_pasokan: str | None = Field(default=None, alias="Jenis Pasokan", description="Kategori legenda peta: Impor, Dari Kilang, atau Dari Fuel Terminal. Pada file saat ini ketiganya digabung sebagai teks ringkasan untuk setiap regional; ini belum membuktikan bahwa semua jenis pasokan tersedia pada setiap regional. Jangan gunakan ringkasan tersebut sebagai hubungan rute yang terverifikasi.")
    node_asal: str | None = Field(default=None, alias="Node Asal", description="Lokasi awal suatu hubungan pasokan apabila dapat ditetapkan dari arah garis peta. Saat ini seluruh nilai null karena pasangan asal-tujuan belum berhasil diverifikasi; null tidak berarti tidak ada pasokan. Kolom ini tidak boleh diisi dari dugaan kedekatan geografis.")
    node_tujuan: str | None = Field(default=None, alias="Node Tujuan", description="Lokasi penerima suatu hubungan pasokan apabila dapat ditetapkan dari arah garis peta. Saat ini seluruh nilai null karena pasangan asal-tujuan belum berhasil diverifikasi; record Rute Pasokan hanya ringkasan regional, bukan rute rinci yang dapat dianalisis sebagai jaringan.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
