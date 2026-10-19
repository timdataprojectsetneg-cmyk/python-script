# Data Dictionary: BGN Satuan Pelayanan Pemenuhan Gizi (SPPG) MBG

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Badan Gizi Nasional (BGN) Satuan Pelayanan Pemenuhan Gizi (SPPG) MBG** pada usecase **Kunjungan Presiden** (Sub Usecase: *Peta dan Profil Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Peta dan Profil Wilayah |
| **Publisher** | Badan Gizi Nasional (BGN) (`bgn`) |
| **Source Name** | `sppg_mbg` |
| **Tipe Akses** | Web Portal & Geospasial GIS GINA BGN |
| **Kebutuhan Registrasi / Login** | **Khusus Koordinasi K/L Pemerintah** |
| **Endpoint Live Sumber** | `https://gina.bgn.go.id/api/v1/sppg` & `https://www.bgn.go.id/` |
| **Frekuensi Update** | Harian / Pemantauan Berjalan |
| **Target Database** | PostgreSQL (`raw_kunker.raw_bgn_sppg_mbg`) |
| **Target Elasticsearch** | `raw_bgn_sppg_mbg` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Peta dan Profil Wilayah.xlsx* (Sheet: *Sebaran MBG*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_sppg` | `String` | kode | Identifier unik Satuan Pelayanan Pemenuhan Gizi (contoh: `SPPG-3302-001`). |
| `nama_sppg` | `String` | - | Nama unit dapur pelayanan makanan bergizi gratis. |
| `provinsi` | `String` | - | Provinsi wilayah operasional dapur. |
| `kabupaten_kota` | `String` | - | Kabupaten atau kota lokasi dapur. |
| `kecamatan` | `String` | - | Kecamatan lokasi dapur. |
| `kapasitas_porsi_harian` | `Integer` | porsi/hari | Kapasitas produksi makanan bergizi per hari. |
| `jumlah_penerima_manfaat` | `Integer` | siswa/balita | Jumlah sasaran penerima manfaat terlayani. |
| `status_operasional` | `String` | - | Status operasional unit dapur (`Aktif`, `Persiapan`, `Uji Coba`). |
| `latitude` | `Float` (Nullable) | derajat | Koordinat lintang lokasi dapur SPPG. |
| `longitude` | `Float` (Nullable) | derajat | Koordinat bujur lokasi dapur SPPG. |
| `data_source` | `String` | - | Default: `Badan Gizi Nasional (BGN)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher bgn
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source sppg_mbg --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_bgn_sppg_mbg.py -v
```
