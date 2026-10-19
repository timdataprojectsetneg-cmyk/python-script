# Data Dictionary: Kemlu Iuran Organisasi Internasional

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Kemlu Iuran Organisasi Internasional** pada usecase **Geopolitik** (Sub Usecase: *Diplomasi Multilateral & Komitmen Internasional*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Diplomasi Multilateral & Komitmen Internasional |
| **Publisher** | Kementerian Luar Negeri RI (DJKSM) & Kementerian Keuangan RI (`kemlu`) |
| **Source Name** | `iuran_organisasi_internasional` |
| **Tipe Akses** | Portal Web Scraping / Satu Data Kemlu & Evaluasi Regulasi Perpres 30/2019 |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://satudata.kemlu.go.id/data/jumlah-keanggotaan-indonesia-dalam-oi` |
| **Frekuensi Update** | Semesteran / Tahunan (Siklus Penganggaran APBN) |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_kemlu_iuran_organisasi_internasional`) |
| **Target Elasticsearch** | `raw_kemlu_iuran_organisasi_internasional` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Data Dictionary - Geopolitik - Diplomasi Multilateral dan Komitmen Internasional.xlsx* (Sheet: *Iuran Organisasi Internasional*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_organisasi` | `String` | kode | Identifier registrasi keanggotaan OI Kemenlu (misal: `OI-UN-001`). |
| `nama_organisasi_internasional` | `String` | - | Nama Organisasi Internasional (OI) yang diikuti Indonesia. |
| `kategori_oi` | `String` | - | Kategori OI (`PBB & Badan Khusus`, `Kerja Sama Kawasan`, `Lembaga Keuangan`, `Komoditas`). |
| `dasar_hukum_keanggotaan` | `String` (Nullable) | - | Regulasi ratifikasi / keanggotaan (Keppres/Perpres). |
| `kl_focal_point` | `String` | - | Kementerian/Lembaga teknis pemegang mandat focal point Republik Indonesia. |
| `besaran_iuran_tahunan_valas` | `Float` | valas | Nominal kewajiban kontribusi iuran tahunan dalam mata uang asing. |
| `mata_uang` | `String` | kode | Mata uang penagihan iuran (`USD`, `GBP`, `EUR`, `CHF`). |
| `ekuivalen_rupiah_miliar` | `Float` | Miliar Rp | Estimasi alokasi anggaran APBN untuk pembayaran iuran. |
| `evaluasi_kemanfaatan` | `String` | - | Hasil audit evaluasi kemanfaatan (`Tinggi / Mandatori`, `Tinggi / Strategis`, `Sedang`). |
| `status_iuran_terakhir` | `String` | - | Status pembayaran tahun berjalan (`Lunas`, `Proses Pencairan`, `Tertunda`). |
| `data_source` | `String` | - | Default: `Kementerian Luar Negeri RI (DJKSM) & Kementerian Keuangan RI (Perpres 30/2019)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher kemlu
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source iuran_organisasi_internasional --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kemlu_iuran_organisasi_internasional.py -v
```
