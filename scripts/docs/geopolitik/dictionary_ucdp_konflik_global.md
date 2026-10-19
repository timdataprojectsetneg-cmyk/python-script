# Data Dictionary: UCDP Peta Konflik Bersenjata Global

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **UCDP Peta Konflik Bersenjata Global** pada usecase **Geopolitik** (Sub Usecase: *Situasi Global dan Kawasan*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Situasi Global dan Kawasan |
| **Publisher** | Uppsala Conflict Data Program, Department of Peace and Conflict Research, Uppsala University (`ucdp`) |
| **Source Name** | `konflik_global` |
| **Tipe Akses** | Direct CSV Stream Georeferenced Event Dataset (GED) |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_8.csv` & `https://ucdp.uu.se/downloads/` |
| **Frekuensi Update** | Mingguan / Bulanan (Candidate GED & Global Releases) |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_ucdp_konflik_global`) |
| **Target Elasticsearch** | `raw_ucdp_konflik_global` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Situasi Global dan Kawasan.xlsx* (Sheet: *Peta Konflik Global*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_konflik` | `String` | kode | Identifier insiden konflik bersenjata resmi UCDP (misal: `AFG-2026-3-951-29` atau `UCDP-2026-091`). |
| `negara` | `String` | - | Negara lokasi terjadinya bentrokan bersenjata atau insiden kekerasan. |
| `kawasan` | `String` | - | Kawasan geografis benua/regional (misal: `Eropa Timur`, `Timur Tengah`, `Asia`, `Afrika`). |
| `aktor_terlibat` | `String` | - | Pihak-pihak yang bertikai (Pemerintah vs Pemberontak, Antar-Milisi, atau Pasukan Bersenjata vs Warga Sipil). |
| `jenis_konflik` | `String` | - | Kategori kekerasan bersenjata: `State-based conflict`, `Non-state conflict`, `One-sided violence`. |
| `tanggal_kejadian` | `String` (Nullable) | Tanggal | Waktu tanggal terjadinya insiden bentrokan (format: `YYYY-MM-DD`). |
| `jumlah_korban_tewas` | `Integer` | jiwa | Estimasi korban jiwa meninggal dunia terverifikasi (`best estimate`). |
| `koordinat_lat` | `Float` (Nullable) | derajat | Titik koordinat lintang geografis lokasi insiden bentrokan. |
| `koordinat_lon` | `Float` (Nullable) | derajat | Titik koordinat bujur geografis lokasi insiden bentrokan. |
| `data_source` | `String` | - | Default: `Uppsala Conflict Data Program (UCDP, Uppsala University)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher ucdp
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source konflik_global --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_ucdp_konflik_global.py -v
```
