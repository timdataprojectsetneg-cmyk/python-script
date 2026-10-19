# Data Dictionary: Kemlu Treaty Room (Database Perjanjian Internasional RI)

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Kemlu Treaty Room (Perjanjian Internasional RI)** pada usecase **Geopolitik** (Sub Usecase: *Hubungan Bilateral*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Hubungan Bilateral |
| **Publisher** | Kementerian Luar Negeri RI (Direktorat Hukum dan Perjanjian Internasional / Treaty Room) (`kemlu`) |
| **Source Name** | `treaty_room` |
| **Tipe Akses** | Web Portal & Basis Data Naskah Perjanjian Internasional Bilateral RI |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://treaty.kemlu.go.id/` & `https://kemlu.go.id/` |
| **Frekuensi Update** | Bulanan / Per Penandatanganan & Ratifikasi Perjanjian Baru |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_kemlu_treaty_room`) |
| **Target Elasticsearch** | `raw_kemlu_treaty_room` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Hubungan Bilateral.xlsx* (Sheet: *Treaty Room Perjanjian*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_perjanjian` | `String` | kode | Nomor registrasi traktat internasional Kemenlu (misal: `TR-2026-US-04`). |
| `negara_mitra` | `String` | - | Negara pihak lawan penandatangan traktat bilateral. |
| `judul_perjanjian` | `String` | - | Judul resmi naskah perjanjian internasional (PI) yang disepakati. |
| `bidang_kerja_sama` | `String` | - | Bidang kerja sama (`Hankam`, `Ekonomi & Energi`, `Teknologi & Ekonomi`, `Maritim`, dll). |
| `tahapan` | `String` | - | Tahap perkembangan traktat (`Negosiasi`, `Ditandatangani`, `Diratifikasi`, `Dilaksanakan`). |
| `tanggal_penandatanganan` | `String` (Nullable) | Tanggal | Waktu resmi penandatanganan dokumen perjanjian (format: `YYYY-MM-DD`). |
| `dasar_pengesahan_uu_perpres` | `String` (Nullable) | - | Nomor regulasi UU atau Perpres pengesahan instrumen ratifikasi. |
| `instansi_penanggung_jawab_kl` | `String` (Nullable) | - | Kementerian atau lembaga teknis pengampu implementasi kesepakatan. |
| `data_source` | `String` | - | Default: `Kementerian Luar Negeri RI (Direktorat Hukum dan Perjanjian Internasional / Treaty Room)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher kemlu
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source treaty_room --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kemlu_treaty_room.py -v
```
