# Data Dictionary: GDACS Kedaruratan Bencana dan Wabah Global

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **GDACS Kedaruratan Bencana Global** pada usecase **Geopolitik** (Sub Usecase: *Situasi Global dan Kawasan*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Situasi Global dan Kawasan |
| **Publisher** | Global Disaster Alert and Coordination System & WHO (`gdacs`) |
| **Source Name** | `kedaruratan_bencana` |
| **Tipe Akses** | RSS / XML Open Feed (tanpa otentikasi) |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://www.gdacs.org/xml/rss.xml` |
| **Frekuensi Update** | Real-time / Tiap Jam |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_gdacs_kedaruratan_bencana`) |
| **Target Elasticsearch** | `raw_gdacs_kedaruratan_bencana` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Geopolitik - Situasi Global dan Kawasan.xlsx* (Sheet: *Kedaruratan Bencana Global*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_peringatan` | `String` | Kode | Identifier unik kedaruratan resmi PBB/GDACS (misal: `GDACS-EQ1571367`, `GDACS-TC1001337`). |
| `nama_kejadian` | `String` | - | Nama judul bencana alam atau kedaruratan kesehatan global. |
| `negara_kawasan` | `String` | - | Negara atau wilayah geografis terdampak (misal: *Papua New Guinea*, *Mexico*, *Central Mid-Atlantic Ridge*). |
| `jenis_kedaruratan` | `String` | - | Kategori bencana: *Gempa Bumi*, *Siklon Tropis / Badai*, *Tsunami & Gempa Laut*, *Banjir Bandang*, *Letusan Gunung Berapi*, *Kebakaran Hutan & Lahan*. |
| `level_waspada` | `String` | Level | Status tingkat risiko resmi GDACS: `Red Alert`, `Orange Alert`, `Green Alert`. |
| `tanggal_kejadian` | `Date` | Tanggal | Waktu awal bencana terdeteksi dalam format ISO `YYYY-MM-DD`. |
| `estimasi_korban_terdampak` | `Integer` (Nullable) | Jiwa | Estimasi jumlah populasi warga yang terdampak langsung. |
| `potensi_imbas_ke_indonesia` | `String` (Nullable) | - | Analisis dampak terhadap keselamatan WNI di wilayah, jalur pelayaran kargo logistik ALKI / Selat Malaka, atau kesiapan misi kemanusiaan RI. |
| `latitude` | `Float` (Nullable) | Derajat | Titik koordinat garis lintang pusat bencana. |
| `longitude` | `Float` (Nullable) | Derajat | Titik koordinat garis bujur pusat bencana. |
| `severity` | `String` (Nullable) | - | Parameter teknis keparahan (misal: *Magnitude 6M, Depth:20.8km*, *Max wind speed 213 km/h*). |
| `kode_event` | `String` (Nullable) | Kode | Kode tipe kejadian GDACS (`EQ`, `TC`, `TS`, `FL`, `VO`, `WF`). |
| `deskripsi` | `String` (Nullable) | - | Narasi lengkap kejadian bencana resmi GDACS. |
| `link_detail` | `String` (Nullable) | URL | Tautan laporan analisis spasial bencana GDACS. |
| `data_source` | `String` | - | Default: `Global Disaster Alert and Coordination System (GDACS)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source kedaruratan_bencana --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_gdacs_kedaruratan_bencana.py -v
```
