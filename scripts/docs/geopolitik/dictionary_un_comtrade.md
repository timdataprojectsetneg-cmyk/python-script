# Data Dictionary: UN Comtrade Ekspor Impor Komoditas Strategis

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **UN Comtrade Ekspor Impor Komoditas Strategis** pada usecase **Geopolitik** (Sub Usecase: *Dampak terhadap Kepentingan Nasional*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Dampak terhadap Kepentingan Nasional |
| **Publisher** | United Nations Statistics Division & BPS (`un`) |
| **Source Name** | `comtrade` |
| **Tipe Akses** | REST API (JSON) UN Comtrade v1 / BPS Exim |
| **Kebutuhan Registrasi / Login** | **Perlu Registrasi / Subscription Key Gratis (`Ocp-Apim-Subscription-Key`)** |
| **Endpoint Live Sumber** | `https://comtradeplus.un.org/TradeFlow` & `https://comtradeapi.un.org/public/v1/preview/C/A/HS` |
| **Dokumentasi API** | `https://comtradeplus.un.org/` |
| **Frekuensi Update** | Bulanan |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_un_comtrade`) |
| **Target Elasticsearch** | `raw_un_comtrade` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional.xlsx* (Sheet: *Ekspor Impor Komoditas*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `periode_bulan` | `String` | YYYY-MM | Periode bulan transaksi perdagangan luar negeri. |
| `kode_hs_2digit` | `String` | kode | Klasifikasi 2 digit HS Code (contoh: `75`, `10`, `15`, `27`, `85`). |
| `deskripsi_komoditas` | `String` | - | Nama kelompok produk strategis (Nikel Smelter, Gandum, CPO, Batubara, Semikonduktor). |
| `arus_perdagangan` | `String` | - | Arus barang: `Ekspor` atau `Impor`. |
| `negara_mitra_utama` | `String` | - | Negara asal impor atau tujuan ekspor terbesar. |
| `volume_ribu_ton` | `Float` | Ribu Ton | Volume fisik barang dalam satuan ribuan ton. |
| `nilai_fob_cif_juta_usd` | `Float` | Juta USD | Nilai perdagangan dalam valuta USD (FOB untuk ekspor, CIF untuk impor). |
| `pertumbuhan_tahunan_pct` | `Float` | % | Pertumbuhan nilai dibanding periode sama tahun sebelumnya. |
| `data_source` | `String` | - | Default: `Badan Pusat Statistik (BPS) & UN Comtrade`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher un
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source comtrade --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_un_comtrade.py -v
```
