# Data Dictionary: GDELT Media Asing

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **GDELT Media Asing** pada usecase **Geopolitik** (Sub Usecase: *Persepsi Internasional & Daya Saing*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Persepsi Internasional & Daya Saing |
| **Publisher** | GDELT Project 2.0 (Global Database of Events, Language, and Tone) (`gdelt`) |
| **Source Name** | `media_asing` |
| **Tipe Akses** | REST JSON API (GDELT DOC 2.0 API) & Big Data News Stream |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://api.gdeltproject.org/api/v2/doc/doc?query=Indonesia...` |
| **Frekuensi Update** | Tiap 15 Menit / Real-time Big Data Stream |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_gdelt_media_asing`) |
| **Target Elasticsearch** | `raw_gdelt_media_asing` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Data Dictionary - Geopolitik - Persepsi Internasional terhadap Indonesia.xlsx* (Sheet: *Liputan Media Asing GDELT*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `tanggal_artikel` | `Date / String` (Nullable) | tanggal | Waktu publikasi artikel berita internasional (format `YYYY-MM-DD`). |
| `judul_berita` | `String` | - | Judul artikel berita media asing mengenai Indonesia. |
| `nama_media_sumber` | `String` | - | Nama kantor berita / media asing (Reuters, Bloomberg, Nikkei Asia, dll.). |
| `negara_asal_media` | `String` (Nullable) | - | Negara basis media penerbit (Jepang, Inggris, AS, dll.). |
| `kawasan_media` | `String` (Nullable) | - | Kawasan geografis asal media (Asia Pasifik, Amerika Utara, Eropa). |
| `topik_utama` | `String` | - | Kategori isu utama (Diplomasi & Geopolitik, Investasi & Nikel, Hankam). |
| `skor_sentimen_gdelt` | `Float` | skor | Skor tone sentimen algoritma GDELT (-10.0 s.d +10.0). |
| `url_artikel` | `String` (Nullable) | URL | Tautan URL artikel berita asli daring. |
| `data_source` | `String` | - | Default: `GDELT Project 2.0 (Global Database of Events, Language, and Tone)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher gdelt
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source media_asing --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_gdelt_media_asing.py -v
```
