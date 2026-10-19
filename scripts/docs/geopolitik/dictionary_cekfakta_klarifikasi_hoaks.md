# Data Dictionary: CekFakta Klarifikasi Hoaks

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **CekFakta Klarifikasi Hoaks** pada usecase **Geopolitik** (Sub Usecase: *Persepsi Internasional & Daya Saing*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Persepsi Internasional & Daya Saing |
| **Publisher** | CekFakta.com, Kementerian Luar Negeri RI & Kementerian Komunikasi dan Digital (`cekfakta`) |
| **Source Name** | `klarifikasi_hoaks` |
| **Tipe Akses** | Web Scraping / Fact-Checking & Counter-Narrative Archive |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://cekfakta.com/` |
| **Frekuensi Update** | Harian / Per Kejadian Beredarnya Isu Global |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_cekfakta_klarifikasi_hoaks`) |
| **Target Elasticsearch** | `raw_cekfakta_klarifikasi_hoaks` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Data Dictionary - Geopolitik - Persepsi Internasional terhadap Indonesia.xlsx* (Sheet: *Cek Fakta & Narasi Global*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_narasi` | `String` | kode | Identifier unik pemantauan narasi internasional (misal: `NAR-2026-01`). |
| `isu_pemberitaan` | `String` | - | Isu atau topik pemberitaan mengenai Indonesia di kancah internasional. |
| `klaim_narasi` | `String` | - | Substansi klaim atau narasi yang beredar di media/ruang publik luar negeri. |
| `asal_media_sumber` | `String` (Nullable) | - | Media internasional atau platform digital asal narasi beredar. |
| `tingkat_sebaran` | `String` | level | Tingkat persebaran isu: `Tinggi (Viral)`, `Sedang`, `Rendah`. |
| `hasil_verifikasi_cek_fakta` | `String` | verdict | Hasil verifikasi: `Konteks Dimanipulasi`, `Fakta Tidak Tepat`, `Disinformasi`. |
| `tanggapan_resmi_pemerintah` | `String` (Nullable) | - | Substansi tanggapan klarifikasi resmi pemerintah Indonesia. |
| `instansi_klarifikasi` | `String` (Nullable) | - | Instansi juru bicara penjelas (Kemenlu RI, Komdigi, Kemenkeu, dll.). |
| `tanggal_klarifikasi` | `Date / String` (Nullable) | tanggal | Waktu publikasi klarifikasi resmi (format `YYYY-MM-DD`). |
| `data_source` | `String` | - | Default: `CekFakta.com, Kementerian Luar Negeri RI & Kementerian Komunikasi dan Digital`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher cekfakta
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source klarifikasi_hoaks --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_cekfakta_klarifikasi_hoaks.py -v
```
