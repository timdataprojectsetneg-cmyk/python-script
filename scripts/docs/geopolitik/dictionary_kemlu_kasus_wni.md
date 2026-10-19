# Data Dictionary: Kemlu Rekapitulasi Kasus Pelindungan WNI

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Kemlu Rekapitulasi Kasus WNI** pada usecase **Geopolitik** (Sub Usecase: *Pelindungan WNI di Luar Negeri*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Pelindungan WNI di Luar Negeri |
| **Publisher** | Kementerian Luar Negeri RI (Direktorat Pelindungan WNI / BHI) (`kemlu`) |
| **Source Name** | `kasus_wni` |
| **Tipe Akses** | Web Portal & Rekapitulasi Kasus Pelindungan Portal Peduli WNI |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://peduliwni.kemlu.go.id/` & `https://kemlu.go.id/` |
| **Frekuensi Update** | Mingguan / Bulanan |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_kemlu_kasus_wni`) |
| **Target Elasticsearch** | `raw_kemlu_kasus_wni` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Pelindungan WNI di Luar Negeri.xlsx* (Sheet: *Rekapitulasi Kasus WNI*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_kasus` | `String` | kode | Nomor registrasi/tiket kasus pelindungan WNI (misal: `PWNI-2026-MY-412`). |
| `negara_kejadian` | `String` | - | Negara tempat timbulnya kasus atau wilayah perwakilan RI penangan. |
| `kategori_kasus` | `String` | - | Kategori kasus (`Ketenagakerjaan / Gaji`, `Keimigrasian`, `TPPO / Online Scam`, `Hukum Pidana`). |
| `jumlah_korban_terlibat` | `Integer` | jiwa | Jumlah estimasi WNI korban atau pihak terkait dalam kasus. |
| `tanggal_pengaduan` | `String` (Nullable) | Tanggal | Waktu tanggal laporan dicatatkan pada perwakilan RI (format: `YYYY-MM-DD`). |
| `status_penanganan` | `String` | - | Status penanganan (`Dalam Proses`, `Mediasi Selesai`, `Repatriasi Selesai`). |
| `bantuan_hukum_diberikan` | `String` (Nullable) | - | Bentuk fasilitasi pendampingan (Safe House, Pengacara Retainer, Fasilitasi SPLP). |
| `data_source` | `String` | - | Default: `Kementerian Luar Negeri RI (Direktorat Pelindungan WNI / BHI)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher kemlu
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source kasus_wni --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kemlu_kasus_wni.py -v
```
