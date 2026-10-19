# Data Dictionary: SP4N-LAPOR! Rekapitulasi Aduan Wilayah

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **SP4N-LAPOR! Rekapitulasi Aduan Wilayah** pada usecase **Kunjungan Kerja Presiden** (Sub Usecase: *Konteks Sosial dan Kelembagaan Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Konteks Sosial dan Kelembagaan Wilayah |
| **Publisher** | Sistem Pengelolaan Pengaduan Pelayanan Publik Nasional - LAPOR! (`lapor`) |
| **Source Name** | `rekap_aduan_wilayah` |
| **Tipe Akses** | REST JSON API Datawarehouse Publik |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://www.lapor.go.id/api/datawarehouse/maps/asal_pelapor` |
| **Frekuensi Update** | Harian / Real-time |
| **Target Database** | PostgreSQL (`raw_kunker.raw_lapor_aduan`) |
| **Target Elasticsearch** | `raw_lapor_aduan` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Konteks Sosial dan Kelembagaan Wilayah.xlsx* (Sheet: *Rekapitulasi Aduan Wilayah*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_aduan` | `String` | Kode | Nomor tiket aduan masyarakat atau kode agregat wilayah SP4N-LAPOR (misal: `ADU-2026-8812`, `LAPOR-3171-2024`). |
| `tanggal_lapor` | `Date / String` | tanggal | Waktu penyampaian laporan masyarakat (format `YYYY-MM-DD`). |
| `kategori_program` | `String` | - | Program terkait keluhan/aspirasi (misal: *Pelayanan Publik & Tata Kelola Wilayah*, *Makan Bergizi Gratis (MBG)*, *Koperasi Desa Merah Putih*, *Bansos*). |
| `provinsi` | `String` | - | Provinsi asal pelapor / wilayah administrasi aduan. |
| `kabupaten_kota` | `String` | - | Kabupaten/Kota asal aduan (misal: *Kota Jakarta Pusat*, *Kabupaten Banyumas*). |
| `uraian_laporan` | `String` | - | Ringkasan substansi keluhan atau rekapitulasi volume pengaduan masyarakat. |
| `status_tindak_lanjut` | `String` | - | Status progres tindak lanjut (`Diverifikasi`, `Ditindaklanjuti`, `Selesai`). |
| `instansi_tujuan` | `String` | - | K/L atau Pemerintah Daerah penanggung jawab penyelesaian. |
| `jumlah_aduan` | `Integer` | aduan | Total volume aduan yang tercatat pada wilayah/periode terkait. |
| `tahun` | `Integer` | tahun | Tahun periode pelaporan (misal: 2024). |
| `kode_wilayah` | `String` (Nullable) | kode | Kode wilayah adm2 BPS/Kemendagri (misal: `31.71`, `33.02`). |
| `data_source` | `String` | - | Default: `SP4N-LAPOR! KemenPANRB, Kemensetneg & KSP`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher lapor
```

### Eksekusi Live Ingestion
```powershell
# Ekstrak 5 wilayah
python run_ingestion.py run --usecase kunjungan_presiden --source rekap_aduan_wilayah --limit 5

# Ekstrak seluruh wilayah nasional (500+ kabupaten/kota)
python run_ingestion.py run --usecase kunjungan_presiden --source rekap_aduan_wilayah
```

### Menjalankan Unit Test
```powershell
pytest tests/unit/test_lapor_rekap_aduan.py -v
```
