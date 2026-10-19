# Data Dictionary: Kemenhub & BIG Infrastruktur Bandara (Hubud Bandara)

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Kemenhub Hubud & BIG Satupeta Bandara** pada usecase **Kunjungan Kerja Presiden** (Sub Usecase: *Kesiapan Kunjungan*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Kesiapan Kunjungan |
| **Publisher** | Kementerian Perhubungan RI & Badan Informasi Geospasial (`kemenhub`) |
| **Source Name** | `hubud_bandara` |
| **Tipe Akses** | ArcGIS REST MapServer (JSON terbuka tanpa otentikasi) |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://kspservices.big.go.id/satupeta/rest/services/PUBLIK/SARANA_PRASARANA/MapServer/4/query` |
| **Frekuensi Update** | Bulanan / Kondisional |
| **Target Database** | PostgreSQL (`raw_kunker.raw_kemenhub_hubud_bandara`) |
| **Target Elasticsearch** | `raw_kemenhub_hubud_bandara` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Kesiapan Kunjungan.xlsx* (Sheet: *Infrastruktur Akses & Bandara*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_fasilitas` | `String` | Kode | Gabungan kode ICAO dan IATA bandar udara (misal: `WARQ / SOC`, `WIHH / HLP`) atau ID unik fasilitas. |
| `nama_fasilitas` | `String` | - | Nama resmi bandar udara atau lanud (misal: *Bandara Adi Sumarmo*, *Bandara Halim Perdanakusuma*). |
| `jenis_infrastruktur` | `String` | - | Klasifikasi tipe (misal: *Bandar Udara Sipil / Komersial*, *Pangkalan Udara TNI AU / Enclave Sipil*). |
| `panjang_runway_m` | `Float` (Nullable) | meter | Panjang landasan pacu utama hasil parsing dimensi runway atau referensi ICAO code. |
| `klasifikasi_pesawat_maks` | `String` | - | Tipe pesawat kritis yang dapat mendarat (misal: *A330-300*, *B737-900 ER*, *ATR72-500*, *C-130 Hercules*). |
| `kondisi_kemantapan_jalan_pct` | `Float` | % | Tingkat kesiapan dan kemantapan operasional fasilitas landasan (default: `100.0%`). |
| `status_kelayakan_vvip` | `String` | - | Evaluasi otomatis kesiapan protokoler/VVIP: `Layak Penuh Pesawat Kenegaraan VVIP (Wide Body / BBJ)`, `Layak Pesawat Kepresidenan BBJ (Narrow Body)`, `Layak Pesawat Taktis VVIP (TNI AU C-130 / CN-295)`, atau `Terbatas Pesawat Ringan / Akses Helikopter VVIP`. |
| `kode_icao` | `String` (Nullable) | Kode | Kode 4 huruf ICAO bandara. |
| `kode_iata` | `String` (Nullable) | Kode | Kode 3 huruf IATA bandara. |
| `klasifikasi_icao` | `String` (Nullable) | Kode | Aerodrome reference code (misal: `4E`, `4D`, `3C`, `2B`). |
| `kekuatan_pcn` | `String` (Nullable) | Indeks | Pavement Classification Number perkerasan landasan pacu (misal: `68 F/C/X/T`). |
| `pengelola` | `String` (Nullable) | - | Instansi pengelola (*UPBU Kemenhub*, *PT Angkasa Pura*, *TNI AU*, *Pemda*). |
| `alamat` | `String` (Nullable) | - | Alamat fisik fasilitas bandara. |
| `jam_operasional` | `String` (Nullable) | - | Jam buka operasional bandara (*24 Jam*, *07.00 - 17.00 WIB*). |
| `kabupaten_kota` | `String` (Nullable) | - | Wilayah administratif kabupaten/kota kedudukan bandara. |
| `latitude` | `Float` (Nullable) | derajat | Titik koordinat garis lintang. |
| `longitude` | `Float` (Nullable) | derajat | Titik koordinat garis bujur. |
| `elevasi_mdpl` | `Float` (Nullable) | meter | Ketinggian bandar udara di atas permukaan laut. |
| `data_source` | `String` | - | Default: `Ditjen Hubud Kemenhub & BIG Satupeta`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source hubud_bandara --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kemenhub_hubud_bandara.py -v
```
