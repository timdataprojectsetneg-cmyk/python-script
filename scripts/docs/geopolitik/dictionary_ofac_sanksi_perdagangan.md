# Data Dictionary: OFAC Sanksi dan Pembatasan Perdagangan Internasional

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **OFAC Sanksi Perdagangan** pada usecase **Geopolitik** (Sub Usecase: *Dampak terhadap Kepentingan Nasional*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Dampak terhadap Kepentingan Nasional |
| **Publisher** | US Department of the Treasury & EU Sanctions (`ofac`) |
| **Source Name** | `sanksi_perdagangan` |
| **Tipe Akses** | Direct CSV Stream Download (tanpa otentikasi) |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV` |
| **Frekuensi Update** | Mingguan / Real-time Perubahan SDN |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_ofac_sanksi_perdagangan`) |
| **Target Elasticsearch** | `raw_ofac_sanksi_perdagangan` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Geopolitik - Dampak terhadap Kepentingan Nasional.xlsx* (Sheet: *Sanksi & Pembatasan Dagang*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_sanksi` | `String` | Kode | Identifier resmi sanksi perdagangan dan embargo (misal: `OFAC-SDN-36`, `OFAC-SDN-306`). |
| `otoritas_penerbit` | `String` | - | Otoritas penerbit: `US Department of the Treasury (OFAC)`. |
| `negara_sasaran` | `String` | - | Negara sasaran sanksi (misal: *Federasi Rusia*, *Iran*, *Kuba*, *Myanmar*, *Korea Utara*). |
| `sektor_terkena` | `String` | - | Sektor ekonomi sasaran: *Sektor Keuangan, Perbankan Devisa & Transaksi SWIFT*, *Sektor Energi, Minyak Mentah & Gas Bumi*, *Sektor Pelayaran Niaga & Armada Logistik Maritim*, *Komponen Elektronik & Semikonduktor Barang Ganda (Dual-Use)*. |
| `tanggal_efektif` | `Date` | Tanggal | Waktu mulai berlakunya pembatasan format ISO `YYYY-MM-DD`. |
| `komoditas_terdampak_indonesia` | `String` | - | Produk atau komoditas ekspor-impor Indonesia yang rawan terimbas sanksi (CPO, pupuk potasium, gandum pangan, barang elektronika). |
| `potensi_dampak_ke_pelaku_usaha` | `String` | - | Analisis risiko sanksi sekunder (*secondary sanctions*) bagi eksportir dan perbankan devisa nasional. |
| `nama_entitas` | `String` | - | Nama resmi korporasi, institusi perbankan, kapal kargo, atau pejabat yang dikenai sanksi SDN. |
| `tipe_entitas` | `String` (Nullable) | - | Klasifikasi entitas: `Entity / Corporate`, `Individual / Pejabat`, `Kapal Kargo / Vessel`, `Pesawat Udara / Aircraft`. |
| `program_sanksi` | `String` (Nullable) | Kode | Kode program sanksi OFAC (`RUSSIA-EO14024`, `IRAN`, `CUBA`, `DPRK`, `SDGT`). |
| `catatan_sanksi` | `String` (Nullable) | - | Keterangan identifikasi entitas (alias nama, nomor IMO kapal, swift code). |
| `data_source` | `String` | - | Default: `US Department of the Treasury (OFAC)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source sanksi_perdagangan --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_ofac_sanksi_perdagangan.py -v
```
