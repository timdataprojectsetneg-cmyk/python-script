# Data Dictionary: ESDM Indonesian Crude Price (ICP) & Acuan Minyak Mentah Global

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **ESDM Harga Minyak Mentah ICP** pada usecase **Geopolitik** (Sub Usecase: *Dampak terhadap Kepentingan Nasional*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Dampak terhadap Kepentingan Nasional |
| **Publisher** | Kementerian Energi dan Sumber Daya Mineral (`esdm`) |
| **Source Name** | `harga_minyak_mentah_icp` |
| **Tipe Akses** | Web Scraping & Multi-source Extraction |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Media Center** | `https://www.esdm.go.id/id/media-center/arsip-berita?keyword=ICP` |
| **Endpoint Portal Ditjen Migas** | `https://migas.esdm.go.id/post/harga-minyak-mentah` |
| **Frekuensi Update** | Bulanan (sesuai penetapan Keputusan Menteri ESDM RI) |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_esdm_harga_minyak_mentah_icp`) |
| **Target Elasticsearch** | `raw_esdm_harga_minyak_mentah_icp` |

---

## 2. Skema Data (Data Dictionary)

Sesuai spesifikasi KAK dan lembar *Alpha Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional.xlsx* (Sheet: *Harga Komoditas ICP dan Pangan*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `periode_data` | `String` | `YYYY-MM` | Periode tahun dan bulan penetapan harga resmi (misal: `2026-09`, `2026-08`). |
| `tahun` | `Integer` | Tahun | Tahun kalender penetapan ICP (misal: `2026`). |
| `bulan` | `String` | - | Nama bulan kalender penetapan (misal: *September*, *Agustus*, *Juli*). |
| `icp_usd` | `Float` | USD/barel | Rata-rata resmi Harga Minyak Mentah Indonesia (Indonesian Crude Price / ICP) per barel. |
| `icp_perubahan_usd` | `Float` (Nullable) | USD/barel | Besaran perubahan harga dibandingkan bulan sebelumnya (+ naik / - turun). |
| `brent_ice_usd` | `Float` (Nullable) | USD/barel | Harga rata-rata minyak mentah acuan Brent (ICE) bulanan. |
| `wti_nymex_usd` | `Float` (Nullable) | USD/barel | Harga rata-rata minyak mentah acuan West Texas Intermediate (Nymex) bulanan. |
| `dated_brent_usd` | `Float` (Nullable) | USD/barel | Harga rata-rata minyak mentah acuan Dated Brent bulanan. |
| `basket_opec_usd` | `Float` (Nullable) | USD/barel | Harga rata-rata Basket OPEC bulanan. |
| `nomor_kepmen` | `String` (Nullable) | - | Nomor Keputusan Menteri ESDM Republik Indonesia penetapan ICP. |
| `faktor_geopolitik_pasar` | `String` (Nullable) | - | Ringkasan sentimen geopolitik, jalur maritim energi, dan dinamika supply/demand global. |
| `sumber_dokumen_url` | `String` (Nullable) | - | URL siaran pers resmi ESDM atau dokumen penetapan Ditjen Migas. |
| `data_source` | `String` | - | Default: `Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source harga_minyak_mentah_icp --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_esdm_harga_minyak_mentah_icp.py -v
```
