# Data Dictionary: KKP Kampung Nelayan Merah Putih (KNMP)

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **KKP Kampung Nelayan Merah Putih (KNMP)** pada usecase **Kunjungan Kerja Presiden** (Sub Usecase: *Peta dan Profil Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Peta dan Profil Wilayah |
| **Publisher** | Kementerian Kelautan dan Perikanan RI (`kkp`) |
| **Source Name** | `kampung_nelayan_merah_putih` |
| **Tipe Akses** | Web Scraping Portal PIPP & Satu Data KKP |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://pipp.kkp.go.id/` (Pusat Informasi Pelabuhan Perikanan) & `https://portaldata.kkp.go.id/` |
| **Frekuensi Update** | Semesteran |
| **Target Database** | PostgreSQL (`raw_kunker.raw_kkp_kampung_nelayan_merah_putih`) |
| **Target Elasticsearch** | `raw_kkp_kampung_nelayan_merah_putih` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Peta dan Profil Wilayah.xlsx* (Sheet: *Sebaran KNMP*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_knmp` | `String` | Kode | Identifier unik sentra Kampung Nelayan Merah Putih (misal: `KNMP-3301-01`). |
| `nama_desa_nelayan` | `String` | - | Nama sentra perikanan, pelabuhan perikanan, atau kampung nelayan pesisir. |
| `provinsi` | `String` | - | Nama provinsi wilayah lokasi pesisir (misal: *Jawa Tengah*, *Jawa Timur*, *Maluku*). |
| `kabupaten_kota` | `String` | - | Nama kabupaten atau kota pesisir (misal: *Cilacap*, *Trenggalek*, *Tual*). |
| `jumlah_nelayan` | `Integer` (Nullable) | Orang | Jumlah nelayan binaan aktif yang terdata di sentra perikanan. |
| `kapasitas_cold_storage_ton` | `Float` (Nullable) | Ton | Kapasitas fasilitas ruang pendingin ikan (cold storage). |
| `produksi_es_ton_hari` | `Float` (Nullable) | Ton/hari | Kapasitas produksi pabrik es balok pendukung mutu tangkapan. |
| `status_operasional` | `String` | - | Status operasional fasilitas sentra (misal: *Beroperasi*, *Pengembangan*, *Persiapan*). |
| `latitude` | `Float` (Nullable) | Derajat | Koordinat lintang geografis lokasi sentra. |
| `longitude` | `Float` (Nullable) | Derajat | Koordinat bujur geografis lokasi sentra. |
| `data_source` | `String` | - | Default: `Kementerian Kelautan dan Perikanan (KKP) Republik Indonesia`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher kkp
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source kampung_nelayan_merah_putih --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kkp_kampung_nelayan_merah_putih.py -v
```
