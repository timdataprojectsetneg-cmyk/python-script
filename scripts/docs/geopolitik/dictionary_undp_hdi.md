# Data Dictionary: UNDP Human Development Index (HDI) Time Series

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **UNDP HDI** pada usecase **Geopolitik** (Sub Usecase: *Persepsi Internasional terhadap Indonesia*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Persepsi Internasional terhadap Indonesia |
| **Publisher** | United Nations Development Programme (`undp`) |
| **Source Name** | `hdi` |
| **Tipe Akses** | Direct CSV Stream Download |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv` |
| **Frekuensi Update** | Tahunan |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_undp_hdi`) |
| **Target Elasticsearch** | `raw_undp_hdi` |

---

## 2. Skema Data (Data Dictionary)

Sesuai spesifikasi KAK dan lembar *Alpha Data Dictionary - Geopolitik - Persepsi Internasional terhadap Indonesia.xlsx* (Sheet: *Indeks Pembangunan Manusia*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `tahun` | `Integer` | Tahun | Tahun observasi metrik pembangunan manusia (misal: `2023`, `2022`, dst). |
| `negara` | `String` | - | Nama negara resmi (misal: *Indonesia*, *Malaysia*, *Singapore*, *China*, *United States*). |
| `iso3` | `String` (Nullable) | - | Kode 3 huruf ISO3 negara (misal: `IDN`, `MYS`, `SGP`, `USA`). |
| `skor_hdi` | `Float` | Indeks | Skor komposit Human Development Index (skala 0.000 - 1.000). |
| `peringkat_hdi_dunia` | `Integer` (Nullable) | Ranking | Peringkat pembangunan manusia global terkini. |
| `angka_harapan_hidup_tahun` | `Float` (Nullable) | Tahun | Angka Harapan Hidup saat lahir (Life Expectancy). |
| `harapan_lama_sekolah_tahun` | `Float` (Nullable) | Tahun | Perkiraan lama sekolah yang diharapkan ditempuh anak usia sekolah (Expected Years of Schooling). |
| `rata_rata_lama_sekolah_tahun` | `Float` (Nullable) | Tahun | Rata-rata lama sekolah riil yang dicapai penduduk usia 25 tahun ke atas (Mean Years of Schooling). |
| `gni_per_kapita_ppp_usd` | `Float` (Nullable) | USD PPP | Pendapatan Nasional Bruto per kapita berbasis daya beli (Purchasing Power Parity). |
| `kategori_hdi` | `String` | - | Klasifikasi pembangunan manusia: *Very High*, *High*, *Medium*, atau *Low Human Development*. |
| `data_source` | `String` | - | Default: `United Nations Development Programme (UNDP) HDR Time Series`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source hdi --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_undp_hdi.py -v
```
