# Data Dictionary: WIPO Global Innovation Index

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **WIPO Global Innovation Index** pada usecase **Geopolitik** (Sub Usecase: *Persepsi Internasional & Daya Saing*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Persepsi Internasional & Daya Saing |
| **Publisher** | World Intellectual Property Organization (`wipo`) |
| **Source Name** | `global_innovation_index` |
| **Tipe Akses** | Web Scraping / Open Data Reports Portal |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://www.wipo.int/en/web/global-innovation-index` |
| **Frekuensi Update** | Tahunan |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_wipo_global_innovation_index`) |
| **Target Elasticsearch** | `raw_wipo_global_innovation_index` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Data Dictionary - Geopolitik - Persepsi Internasional terhadap Indonesia.xlsx* (Sheet: *Indeks Inovasi Global WIPO*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `tahun` | `Integer` | tahun | Tahun pemeringkatan indeks inovasi global (misal: `2026`). |
| `skor_gii_indonesia` | `Float` | skor (0-100) | Skor komposit Global Innovation Index Indonesia. |
| `peringkat_gii_indonesia` | `Integer` | peringkat | Peringkat Indonesia di antara 133 ekonomi dunia. |
| `peringkat_asean` | `Integer` | peringkat | Peringkat inovasi di kawasan regional ASEAN. |
| `pilar_institusi` | `Float` | skor | Skor pilar kelembagaan institusi (*Institutions*). |
| `pilar_human_capital` | `Float` | skor | Skor pilar modal manusia & riset (*Human Capital & Research*). |
| `pilar_infrastruktur` | `Float` | skor | Skor pilar infrastruktur inovasi (*Infrastructure*). |
| `pilar_market_sophistication` | `Float` | skor | Skor pilar kecanggihan pasar (*Market Sophistication*). |
| `pilar_business_sophistication` | `Float` | skor | Skor pilar kecanggihan bisnis (*Business Sophistication*). |
| `pilar_knowledge_technology` | `Float` | skor | Skor pilar keluaran pengetahuan & teknologi (*Knowledge & Tech*). |
| `pilar_creative_outputs` | `Float` | skor | Skor pilar luaran kreatif (*Creative Outputs*). |
| `data_source` | `String` | - | Default: `World Intellectual Property Organization (WIPO)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher wipo
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source global_innovation_index --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_wipo_global_innovation_index.py -v
```
