# Data Dictionary: Kemenkop SIMKOPDES (Koperasi Desa Merah Putih) per Wilayah

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Kemenkop SIMKOPDES (Koperasi Desa Merah Putih)** pada usecase **Kunjungan Kerja Presiden** (Sub Usecase: *Peta dan Profil Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Peta dan Profil Wilayah |
| **Publisher** | Kementerian Koperasi RI (Sistem Informasi Manajemen Koperasi Desa) (`kemenkop`) |
| **Source Name** | `simkopdes_kdmp` |
| **Tipe Akses** | Web Portal & REST API Data Sebaran Sentra Koperasi Desa Merah Putih |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka / Akun Dinas Terbatas**<br>*(Catatan: Indikator agregat nasional dan per provinsi terbuka tanpa login; rincian transaksi mikro internal koperasi memerlukan otentikasi dinas/SIMKOPDES)* |
| **Endpoint Live Sumber** | `https://simkopdes.go.id/` & `https://api.simkopdes.go.id/api/provinces` |
| **Frekuensi Update** | Near real-time (tiap 30 menit / per agregasi berkala) |
| **Target Database** | PostgreSQL (`raw_kunker.raw_kemenkop_simkopdes_kdmp`) |
| **Target Elasticsearch** | `raw_kemenkop_simkopdes_kdmp` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Peta dan Profil Wilayah.xlsx* (Sheet: *Sebaran KDMP*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `provinsi` | `String` | - | Nama provinsi wilayah kerja binaan koperasi. |
| `provinsi_id` | `Integer` (Nullable) | - | Kode identifier provinsi (Kemendagri / SIMKOPDES). |
| `kabupaten_kota` | `String` | - | Nama kabupaten atau kota sentra sebaran koperasi. |
| `total_koperasi` | `Integer` | unit | Jumlah unit Koperasi Desa Merah Putih (KDMP) yang terbentuk. |
| `koperasi_sehat` | `Integer` | unit | Jumlah unit koperasi dengan predikat kesehatan usaha 'Sehat'. |
| `koperasi_cukup_sehat` | `Integer` | unit | Jumlah unit koperasi dengan predikat 'Cukup Sehat'. |
| `koperasi_tidak_sehat` | `Integer` | unit | Jumlah unit koperasi yang belum dinilai atau berkategori 'Tidak Sehat'. |
| `total_anggota` | `Integer` | orang | Total akumulasi masyarakat anggota koperasi desa terdaftar. |
| `omzet_pendapatan` | `Float` | Rupiah | Total nilai omzet transaksi perputaran usaha ekonomi koperasi. |
| `latitude` | `Float` (Nullable) | derajat | Titik koordinat lintang geografis lokasi wilayah/sentra koperasi. |
| `longitude` | `Float` (Nullable) | derajat | Titik koordinat bujur geografis lokasi wilayah/sentra koperasi. |
| `data_source` | `String` | - | Default: `Kementerian Koperasi RI (Sistem Informasi Manajemen Koperasi Desa / SIMKOPDES)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher kemenkop
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source simkopdes_kdmp --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kemenkop_simkopdes_kdmp.py -v
```
