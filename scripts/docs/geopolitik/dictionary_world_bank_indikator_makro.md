# Data Dictionary: World Bank Indikator Makroekonomi & Profil Negara Mitra

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **World Bank Indikator Makroekonomi** pada usecase **Geopolitik** (Sub Usecase: *Hubungan Bilateral*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Hubungan Bilateral |
| **Publisher** | World Bank (`world_bank`) |
| **Source Name** | `indikator_makro` |
| **Tipe Akses** | REST JSON API Publik (World Bank Open Data API) |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://api.worldbank.org/v2/country/IDN;CHN;USA;JPN;SGP;MYS;IND;AUS;KOR;DEU/indicator/SP.POP.TOTL;NY.GDP.MKTP.CD;NY.GDP.PCAP.CD;NY.GDP.MKTP.KD.ZG;FP.CPI.TOTL.ZG?source=2&format=json&per_page=1000` |
| **Frekuensi Update** | Tahunan / Semesteran |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_world_bank_indikator_makro`) |
| **Target Elasticsearch** | `raw_world_bank_indikator_makro` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Geopolitik - Hubungan Bilateral.xlsx* (Sheet: *Profil Mitra & Indikator Makro*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `negara` | `String` | - | Nama negara mitra diplomatik atau komparator (misal: *Indonesia*, *Jepang*, *Tiongkok*, *Amerika Serikat*). |
| `kode_iso3` | `String` | Kode | Kode resmi 3 huruf ISO3 negara (misal: `IDN`, `JPN`, `CHN`, `USA`). |
| `kawasan` | `String` (Nullable) | - | Kawasan geografis (*Asia Tenggara*, *Asia Timur*, *Amerika Utara*, *Eropa Barat*, dll.). |
| `tahun` | `Integer` | Tahun | Tahun observasi indikator makroekonomi (misal: `2024`, `2023`). |
| `populasi_juta_jiwa` | `Float` (Nullable) | Juta jiwa | Total jumlah penduduk negara (WDI: `SP.POP.TOTL` / 1.000.000). |
| `pdb_nominal_miliar_usd` | `Float` (Nullable) | Miliar USD | PDB nominal pada harga berlaku (WDI: `NY.GDP.MKTP.CD` / 1.000.000.000). |
| `pdb_per_kapita_usd` | `Float` (Nullable) | USD | Produk Domestik Bruto per kapita (WDI: `NY.GDP.PCAP.CD`). |
| `pertumbuhan_pdb_pct` | `Float` (Nullable) | % | Laju pertumbuhan ekonomi riil tahunan (WDI: `NY.GDP.MKTP.KD.ZG`). |
| `inflasi_pct` | `Float` (Nullable) | % | Tingkat inflasi indeks harga konsumen tahunan (WDI: `FP.CPI.TOTL.ZG`). |
| `nilai_ekspor_ri_ke_mitra_usd` | `Float` (Nullable) | USD | Nilai ekspor barang dan jasa Indonesia ke negara mitra. |
| `nilai_impor_ri_dari_mitra_usd` | `Float` (Nullable) | USD | Nilai impor barang dan jasa Indonesia dari negara mitra. |
| `neraca_perdagangan_ri_usd` | `Float` (Nullable) | USD | Neraca perdagangan bilateral RI (Ekspor - Impor). |
| `data_source` | `String` | - | Default: `World Bank Open Data (World Development Indicators)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher world_bank
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source indikator_makro --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_world_bank_indikator_makro.py -v
```
