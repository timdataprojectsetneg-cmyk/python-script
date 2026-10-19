# Data Dictionary: CSIS AMTI Insiden Maritim Indo-Pasifik

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **CSIS AMTI Insiden Maritim Indo-Pasifik** pada usecase **Geopolitik** (Sub Usecase: *Situasi Global & Kawasan*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Situasi Global & Kawasan |
| **Publisher** | Center for Strategic and International Studies - Asia Maritime Transparency Initiative (`csis`) |
| **Source Name** | `amti_insiden_maritim` |
| **Tipe Akses** | Web Scraping / Maritime Incident Tracker Portal |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://amti.csis.org/tracker/` & `https://amti.csis.org/` |
| **Frekuensi Update** | Mingguan / Per Kejadian Insiden Maritim |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_csis_amti_insiden_maritim`) |
| **Target Elasticsearch** | `raw_csis_amti_insiden_maritim` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Data Dictionary - Geopolitik - Situasi Global dan Kawasan.xlsx* (Sheet: *Insiden Maritim Indo-Pasifik*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_insiden` | `String` | kode | Identifier unik kejadian insiden maritim (misal: `INS-AMTI-2026-08`). |
| `tanggal_kejadian` | `Date / String` (Nullable) | tanggal | Waktu kejadian insiden maritim berlangsung (format `YYYY-MM-DD`). |
| `wilayah_perairan` | `String` | - | Kawasan perairan strategis (Laut China Selatan, Selat Malaka, Laut Natuna Utara, dll.). |
| `jenis_kejadian` | `String` | - | Jenis insiden maritim (Manuver Kapal Milisi Maritim, Latihan Tembak Amunisi Aktif, dll.). |
| `pihak_terlibat` | `String` | - | Negara atau armada militer / penjaga pantai yang terlibat (misal: `Tiongkok vs Filipina`). |
| `koordinat_lat` | `Float` | derajat | Koordinat lintang insiden maritim. |
| `koordinat_lon` | `Float` | derajat | Koordinat bujur insiden maritim. |
| `tingkat_eskalasi` | `String` | level | Tingkat eskalasi ketegangan: `Tinggi`, `Sedang`, `Rendah`. |
| `catatan_analisis` | `String` (Nullable) | - | Catatan analisis implikasi terhadap keamanan pelayaran & kedaulatan laut nasional. |
| `data_source` | `String` | - | Default: `CSIS Asia Maritime Transparency Initiative (AMTI) & Kemhan RI`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher csis
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source amti_insiden_maritim --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_csis_amti_insiden_maritim.py -v
```
