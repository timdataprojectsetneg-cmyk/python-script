# Data Dictionary: Kemenkes SIRANAP Rumah Sakit Rujukan Medis VVIP

Dokumen ini mendefinisikan skema data, arsitektur scraping, normalisasi, dan integrasi untuk modul **Kemenkes SIRANAP RS Rujukan** pada usecase **Kunjungan Kerja Presiden** (Sub Usecase: *Kesiapan Kunjungan*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Kesiapan Kunjungan |
| **Publisher** | Kementerian Kesehatan RI (`kemenkes`) |
| **Source Name** | `siranap_rs_rujukan` |
| **Tipe Akses** | Web Scraping (HTML terbuka tanpa otentikasi) |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://keslan.kemkes.go.id/app/siranap/rumah_sakit` |
| **Frekuensi Update** | Real-time / Tiap Jam |
| **Target Database** | PostgreSQL (`raw_kunker.raw_kemenkes_siranap_rs_rujukan`) |
| **Target Elasticsearch** | `raw_kemenkes_siranap_rs_rujukan` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Kesiapan Kunjungan.xlsx* (Sheet: *Fasilitas Kesehatan Rujukan*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `kode_rs` | `String` | Kode | Kode registrasi resmi fasyankes Kementerian Kesehatan (misal: `3171012`, `3302012`). |
| `nama_rumah_sakit` | `String` | - | Nama resmi rumah sakit rujukan terdekat (misal: *RSUP Fatmawati*, *RS Umum AL Cilandak*). |
| `kelas_rs` | `String` | - | Klasifikasi tipe rumah sakit: `Kelas A (Rujukan Utama / Nasional)`, `RS Kedinasan TNI/Polri (Mitra VVIP Utama)`, `Kelas B (Rujukan Daerah Terverifikasi)`, atau `RS Swasta / Umum`. |
| `jarak_dari_lokasi_km` | `Float` | km | Estimasi radius jarak tempuh dari titik sentral kunker (default: `4.5 km`). |
| `waktu_tempuh_menit` | `Integer` | menit | Estimasi waktu tempuh iring-iringan darurat medis kepresidenan (default: `12 menit`). |
| `ketersediaan_icu_vvip` | `Integer` | Bed | Jumlah tempat tidur kategori ICU, ICCU, VVIP, dan VIP yang berstatus kosong/siap pakai. |
| `bed_occupancy_rate_pct` | `Float` | % | Estimasi Bed Occupancy Rate (BOR %) berdasarkan kapasitas ruang rawat inap. |
| `kesiapan_ambulans_vvip` | `String` | - | Status kesiapsiagaan mini-ICU ambulans kepresidenan (default: `Siap Siaga 24 Jam`). |
| `alamat_rs` | `String` (Nullable) | - | Alamat jalan rumah sakit. |
| `total_bed_kosong` | `Integer` | Bed | Total seluruh tempat tidur rawat inap kosong dari seluruh kamar. |
| `total_ruangan_terdata` | `Integer` | Unit | Total jumlah ruangan kamar rawat inap terdata pada SIRANAP. |
| `provinsi` | `String` (Nullable) | - | Nama provinsi kedudukan rumah sakit. |
| `kabupaten_kota` | `String` (Nullable) | - | Nama kabupaten/kota kedudukan rumah sakit. |
| `data_source` | `String` | - | Default: `Kementerian Kesehatan RI - SIRANAP`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source siranap_rs_rujukan --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kemenkes_siranap_rs_rujukan.py -v
```
