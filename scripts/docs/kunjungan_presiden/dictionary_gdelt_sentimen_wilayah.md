# Data Dictionary: GDELT Sentimen Wilayah Program Prioritas

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **GDELT Sentimen Wilayah Program Prioritas** pada usecase **Kunjungan Presiden** (Sub Usecase: *Konteks Sosial dan Kelembagaan Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Konteks Sosial dan Kelembagaan Wilayah |
| **Publisher** | OSINT (GDELT Project 2.0 & Media Monitoring Nasional) (`gdelt`) |
| **Source Name** | `sentimen_wilayah` |
| **Tipe Akses** | REST API (JSON) GDELT DOC 2.0 API & Analisis Sentimen |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://api.gdeltproject.org/api/v2/doc/doc?query=Indonesia%20(MBG%20OR%20koperasi%20OR%20stunting)&mode=artlist&format=json&maxrecords=50&sort=datedesc` |
| **Dokumentasi API** | `https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/` |
| **Frekuensi Update** | Real-time / Harian |
| **Target Database** | PostgreSQL (`raw_kunker.raw_gdelt_sentimen_wilayah`) |
| **Target Elasticsearch** | `raw_gdelt_sentimen_wilayah` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Konteks Sosial dan Kelembagaan Wilayah.xlsx* (Sheet: *Sentimen Program Prioritas*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `tanggal_pemantauan` | `Date / String` (Nullable) | tanggal | Waktu monitoring percakapan publik (format `YYYY-MM-DD`). |
| `nama_program_prioritas` | `String` | - | Program prioritas (Makan Bergizi Gratis (MBG), Koperasi Desa Merah Putih, Penurunan Stunting, Cek Kesehatan Gratis (CKG), PSN Ketahanan Pangan, dll.). |
| `provinsi_wilayah` | `String` | - | Provinsi sasaran pemantauan isu (Jawa Tengah, Jawa Barat, NTT, Papua, dll.). |
| `volume_percakapan_media` | `Integer` | artikel/post | Jumlah mention dan artikel yang beredar di media massa & digital. |
| `sentimen_positif_pct` | `Float` | % | Proporsi sentimen positif publik. |
| `sentimen_netral_pct` | `Float` | % | Proporsi sentimen netral publik. |
| `sentimen_negatif_pct` | `Float` | % | Proporsi sentimen kritis / negatif publik. |
| `isu_dominan_diperbincangkan` | `String` (Nullable) | - | Substansi narasi utama di ruang publik lokal. |
| `kanal_utama_sumber` | `String` (Nullable) | - | Kanal percakapan terbanyak (Media Daring, X/Twitter, Instagram, Portal Berita). |
| `data_source` | `String` | - | Default: `GDELT Project 2.0 & Media Monitoring Nasional`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher gdelt
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source sentimen_wilayah --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_gdelt_sentimen_wilayah.py -v
```
