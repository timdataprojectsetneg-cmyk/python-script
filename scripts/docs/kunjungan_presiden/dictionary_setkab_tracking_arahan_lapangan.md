# Data Dictionary: Setkab Tracking Arahan Lapangan

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Setkab Tracking Arahan Lapangan** pada usecase **Kunjungan Presiden** (Sub Usecase: *Janji, Arahan, dan Tindak Lanjut Presiden*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Janji, Arahan, dan Tindak Lanjut Presiden |
| **Publisher** | Sekretariat Kabinet RI (Deputi Bidang Persidangan Kabinet) (`setkab`) |
| **Source Name** | `tracking_arahan_lapangan` |
| **Tipe Akses** | Warta Kunker & Siaran Pers Arahan Lapangan Presiden |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://setkab.go.id/kategori/berita/` & `https://setkab.go.id/` |
| **Frekuensi Update** | Bulanan / Per Kunjungan Kerja Lapangan |
| **Target Database** | PostgreSQL (`raw_kunker.raw_setkab_tracking_arahan_lapangan`) |
| **Target Elasticsearch** | `raw_setkab_tracking_arahan_lapangan` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Janji, Arahan, dan Tindak Lanjut Presiden per Wilayah.xlsx* (Sheet: *Tracking Tindak Lanjut Arahan*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_arahan` | `String` | kode | Identifier unik arahan kunker (misal: `ARH-2026-041`). |
| `tanggal_arahan` | `Date / String` (Nullable) | tanggal | Waktu penyampaian arahan saat kunjungan (format `YYYY-MM-DD`). |
| `lokasi_kunjungan` | `String` | - | Titik lokasi atau kabupaten/kota penyampaian instruksi presiden. |
| `isi_arahan_presiden` | `String` | - | Petunjuk teknis atau instruksi Presiden kepada K/L atau kepala daerah. |
| `instansi_pelaksana` | `String` | - | Instansi teknis K/L/Pemda pengampu pelaksanaan tindak lanjut. |
| `dokumen_dasar_tindak_lanjut` | `String` (Nullable) | - | Surat edaran, inpres, atau keputusan menteri penindak lanjut. |
| `status_tindak_lanjut` | `String` | status | Status tindak lanjut: `Tercapai`, `Sedang Berjalan`, `Perlu Koordinasi`. |
| `data_source` | `String` | - | Default: `Sekretariat Kabinet RI (Deputi Bidang Persidangan Kabinet)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher setkab
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source tracking_arahan_lapangan --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_setkab_tracking_arahan_lapangan.py -v
```
