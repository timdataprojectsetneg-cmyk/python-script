# Data Dictionary: Kemendagri Susunan Pemerintahan Daerah

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Kemendagri Susunan Pemerintahan Daerah** pada usecase **Kunjungan Kerja Presiden** (Sub Usecase: *Konteks Sosial dan Kelembagaan Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Konteks Sosial dan Kelembagaan Wilayah |
| **Publisher** | Kementerian Dalam Negeri RI (Ditjen Otonomi Daerah & Pusdatin PELITA) (`kemendagri`) |
| **Source Name** | `susunan_pemerintahan_daerah` |
| **Tipe Akses** | Web Portal & Database Rilis Pejabat Eksekutif & Legislatif Daerah |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://otda.kemendagri.go.id/` & `https://pelita.kemendagri.go.id/pemda` |
| **Frekuensi Update** | Per Pelantikan / Perubahan Pejabat Kepala Daerah & Pimpinan DPRD |
| **Target Database** | PostgreSQL (`raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah`) |
| **Target Elasticsearch** | `raw_kemendagri_susunan_pemerintahan_daerah` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Konteks Sosial dan Kelembagaan Wilayah.xlsx* (Sheet: *Susunan Pemerintahan Daerah*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `kode_daerah` | `String` | kode | Kode wilayah administrasi Kemendagri (misal: `33.02`). |
| `provinsi` | `String` | - | Nama provinsi tempat kabupaten/kota berada. |
| `kabupaten_kota` | `String` | - | Nama kabupaten atau kota administrasi. |
| `nama_kepala_daerah` | `String` | - | Nama lengkap Bupati / Walikota / Gubernur / Penjabat (Pj) Kepala Daerah. |
| `status_jabatan` | `String` | - | Status jabatan kepala daerah (`Definitif`, `Penjabat (Pj)`, `Pelaksana Tugas (Plt)`). |
| `partai_pengusung_koalisi` | `String` (Nullable) | - | Partai politik atau gabungan koalisi partai pengusung saat Pilkada / penugasan dinas. |
| `nama_ketua_dprd` | `String` (Nullable) | - | Nama Ketua DPRD Kabupaten/Kota. |
| `partai_ketua_dprd` | `String` (Nullable) | - | Partai politik asal Ketua DPRD. |
| `komposisi_kursi_dprd` | `String` (Nullable) | - | Distribusi tekstual perolehan kursi partai di DPRD. |
| `data_source` | `String` | - | Default: `Kementerian Dalam Negeri RI (Ditjen Otonomi Daerah & Pusdatin PELITA)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher kemendagri
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source susunan_pemerintahan_daerah --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kemendagri_susunan_pemda.py -v
```
