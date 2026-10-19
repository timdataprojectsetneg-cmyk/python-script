# Data Dictionary: Kemlu RI Imbauan Perjalanan (Safe Travel)

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Kemlu RI Safe Travel Appeals** pada usecase **Geopolitik** (Sub Usecase: *Pelindungan WNI di Luar Negeri*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik |
| **Sub Usecase** | Pelindungan WNI di Luar Negeri |
| **Publisher** | Kementerian Luar Negeri RI (`kemlu`) |
| **Source Name** | `safe_travel` |
| **Tipe Akses** | REST API (JSON terbuka tanpa otentikasi) |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://safetravel.kemlu.go.id/api/appeal` |
| **Frekuensi Update** | Per Kejadian / Mingguan |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_kemlu_safe_travel`) |
| **Target Elasticsearch** | `raw_kemlu_safe_travel` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Geopolitik - Pelindungan WNI di Luar Negeri.xlsx*:

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `negara` | `String` | - | Negara sasaran imbauan resmi perjalanan (misal: *Iran*, *Nepal*, *Kolombia*, *Viet Nam*). Dideteksi dari `news_country_names` atau teks judul. |
| `kawasan` | `String` | - | Kawasan geografis global (misal: *Asia Tenggara*, *Asia Selatan*, *Timur Tengah*, *Eropa*, *Amerika Latin*, *Afrika*). |
| `level_peringatan` | `String` | Kategori | Tingkat keamanan resmi: `Level 1 - Aman (Hijau)`, `Level 2 - Waspada (Kuning)`, `Level 3 - Hati-hati (Oranye)`, `Level 4 - Bahaya / Hindari (Merah)`. |
| `ringkasan_imbauan` | `String` | - | Substansi imbauan resmi bagi WNI yang telah dibersihkan dari HTML entities/formatting. |
| `tanggal_rilis` | `Date` | Tanggal | Tanggal rilis imbauan dalam format standar ISO `YYYY-MM-DD`. |
| `pemicu_peringatan` | `String` | - | Kategori risiko pemicu: *Bencana Alam*, *Wabah Penyakit / Krisis Kesehatan*, *Konflik Bersenjata & Kerawanan Keamanan*, *Kebijakan Keimigrasian & Perjalanan*. |
| `nomor_hotline_kbri_kjri` | `String` (Nullable) | Kontak | Nomor kontak darurat perwakilan RI setempat (KBRI / KJRI) jika tercantum pada siaran resmi. |
| `news_id` | `String` | UUID | ID unik internal siaran berita Kemlu. |
| `uuid` | `String` | UUID | UUID berita portal Safe Travel. |
| `news_title` | `String` | - | Judul lengkap siaran pers imbauan perjalanan Kemlu. |
| `news_info` | `String` | - | Kategori informasi portal Kemlu (*Keamanan*, *Keimigrasian*, *Asuransi dan Kesehatan*, *Informasi Umum*). |
| `news_image_path` | `String` (Nullable) | URL | URL poster atau dokumen visual imbauan. |
| `news_total_read` | `Integer` | Counter | Total keterbacaan artikel imbauan pada portal Safe Travel. |
| `data_source` | `String` | - | Default: `Kementerian Luar Negeri RI - Portal Safe Travel`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source safe_travel --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kemlu_safe_travel.py -v
```
