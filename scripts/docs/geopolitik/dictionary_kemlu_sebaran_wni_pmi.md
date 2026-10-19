# Data Dictionary: Kemlu Sebaran WNI & PMI di Luar Negeri

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Kemlu Sebaran WNI & PMI** pada usecase **Geopolitik** (Sub Usecase: *Pelindungan WNI di Luar Negeri*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Pelindungan WNI di Luar Negeri |
| **Publisher** | Kementerian Luar Negeri RI (Direktorat PWNI) & Kementerian Perlindungan Pekerja Migran Indonesia (KP2MI) (`kemlu`) |
| **Source Name** | `sebaran_wni_pmi` |
| **Tipe Akses** | Web Portal & Basis Data Lapor Diri Portal Peduli WNI Satu Data Kemlu |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://satudata.kemlu.go.id/data/jumlah-persebaran-wni-lapor-diri-2018-2025` |
| **Frekuensi Update** | Bulanan / Semesteran |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_kemlu_sebaran_wni_pmi`) |
| **Target Elasticsearch** | `raw_kemlu_sebaran_wni_pmi` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Pelindungan WNI di Luar Negeri.xlsx* (Sheet: *Sebaran WNI & PMI*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `negara` | `String` | - | Negara tempat tinggal atau penempatan WNI / PMI. |
| `kawasan` | `String` | - | Kawasan geografis perwakilan (misal: `Asia Tenggara`, `Timur Tengah`, `Amerika Utara`, `Eropa Barat`). |
| `jumlah_wni_lapor_diri` | `Integer` | jiwa | Total akumulasi WNI yang aktif melakukan lapor diri pada Portal Peduli WNI. |
| `pekerja_migran_pmi` | `Integer` | jiwa | Jumlah estimasi Pekerja Migran Indonesia (PMI) resmi terdaftar. |
| `pelajar_mahasiswa` | `Integer` | jiwa | Jumlah pelajar dan mahasiswa Indonesia di negara bersangkutan. |
| `staf_profesional_ekspat` | `Integer` | jiwa | Jumlah staf profesional, diaspora, atau ekspatriat Indonesia. |
| `perwakilan_ri_pengampu` | `String` | - | Nama KBRI / KJRI / KRI yang membawahi wilayah hukum penempatan. |
| `data_source` | `String` | - | Default: `Kementerian Luar Negeri RI & Kementerian Perlindungan Pekerja Migran Indonesia (KP2MI)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher kemlu
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source sebaran_wni_pmi --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kemlu_sebaran_wni_pmi.py -v
```
