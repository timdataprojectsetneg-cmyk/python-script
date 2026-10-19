# Data Dictionary: Setpres Pertemuan Bilateral

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Setpres Pertemuan Bilateral** pada usecase **Geopolitik** (Sub Usecase: *Hubungan Bilateral*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Hubungan Bilateral |
| **Publisher** | Sekretariat Presiden RI & Kementerian Luar Negeri RI (`setpres`) |
| **Source Name** | `pertemuan_bilateral` |
| **Tipe Akses** | Web Portal & Siaran Pers Kunjungan Kenegaraan |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://www.setneg.go.id/baca/index/kunjungan_kenegaraan` & `https://www.presidenri.go.id/siaran-pers/` |
| **Frekuensi Update** | Per Kejadian / Real-time Kunjungan Kerja Luar Negeri & Tamu Negara |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_setpres_pertemuan_bilateral`) |
| **Target Elasticsearch** | `raw_setpres_pertemuan_bilateral` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Data Dictionary - Geopolitik - Hubungan Bilateral.xlsx* (Sheet: *Riwayat Pertemuan Bilateral*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_pertemuan` | `String` | kode | Identifier unik pertemuan diplomatik bilateral (misal: `BIL-2026-01`). |
| `tanggal_kegiatan` | `Date / String` (Nullable) | tanggal | Waktu pertemuan diplomatik berlangsung (format `YYYY-MM-DD`). |
| `negara_mitra` | `String` | - | Negara mitra diplomatik dalam pertemuan. |
| `lokasi_kota_negara` | `String` | - | Tempat terselenggaranya pertemuan (misal: `Istana Singapura`, `Canberra, Australia`). |
| `format_pertemuan` | `String` | - | Format pertemuan (Kunjungan Kenegaraan, KTT Bilateral, Pertemuan Sela-sela KTT). |
| `tokoh_pemimpin_mitra` | `String` | - | Nama Kepala Negara / Kepala Pemerintahan negara mitra. |
| `isu_utama_dibahas` | `String` (Nullable) | - | Fokus substansi bahasan (Investasi EBT, Kerja Sama Pertahanan, IKN Nusantara). |
| `kesepakatan_konkret` | `String` (Nullable) | - | Hasil deliverables atau dokumen kesepakatan/MoU yang disepakati bersama. |
| `data_source` | `String` | - | Default: `Sekretariat Presiden RI & Kementerian Luar Negeri RI`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher setpres
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source pertemuan_bilateral --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_setpres_pertemuan_bilateral.py -v
```
