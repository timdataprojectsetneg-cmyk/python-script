# Data Dictionary: SIPRI Database Belanja Militer Internasional

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **SIPRI Belanja Militer** pada usecase **Geopolitik** (Sub Usecase: *Hubungan Bilateral*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Hubungan Bilateral |
| **Publisher** | Stockholm International Peace Research Institute (`sipri`) |
| **Source Name** | `belanja_militer` |
| **Tipe Akses** | Direct Excel File Download (tanpa otentikasi) |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://www.sipri.org/sites/default/files/SIPRI-Milex-data-1949-2024.xlsx` |
| **Frekuensi Update** | Tahunan |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_sipri_belanja_militer`) |
| **Target Elasticsearch** | `raw_sipri_belanja_militer` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Geopolitik - Hubungan Bilateral.xlsx* (Sheet: *Belanja Militer SIPRI*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `negara` | `String` | - | Nama negara mitra diplomatik atau tetangga kawasan (misal: *Indonesia*, *Singapura*, *Australia*, *China*, *United States*). |
| `tahun` | `Integer` | Tahun | Tahun observasi anggaran pertahanan (misal: `2024`, `2023`, `2022`). |
| `belanja_militer_juta_usd` | `Float` | Juta USD | Total belanja militer dalam satuan Juta US Dollar (Current Prices). |
| `belanja_militer_pct_pdb` | `Float` (Nullable) | % | Porsi anggaran belanja pertahanan terhadap Produk Domestik Bruto / PDB (%). |
| `belanja_militer_pct_apbn` | `Float` (Nullable) | % | Porsi belanja militer terhadap total belanja pemerintah / APBN (%). |
| `peringkat_belanja_dunia` | `Integer` (Nullable) | Ranking | Estimasi peringkat besaran belanja militer global pada tahun anggaran bersangkutan. |
| `tren_modernisasi_alutsista` | `String` (Nullable) | - | Fokus modernisasi alutsista negara (misal: *Modernisasi Jet Tempur Rafale/F-15EX*, *Kapal Selam Nuklir AUKUS*, *Kapal Induk Type 003*). |
| `kawasan` | `String` (Nullable) | - | Kawasan geopolitik (*Asia Tenggara*, *Asia Timur*, *Asia Selatan*, *Oseania*, *Eropa*, *Amerika Utara*, *Timur Tengah*). |
| `data_source` | `String` | - | Default: `Stockholm International Peace Research Institute (SIPRI)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source belanja_militer --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_sipri_belanja_militer.py -v
```
