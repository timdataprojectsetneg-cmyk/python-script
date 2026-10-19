# Data Dictionary: Setpres Statistik & Riwayat Kunjungan Kerja Presiden per Wilayah

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Setpres Statistik Kunjungan Kerja Presiden** pada usecase **Kunjungan Kerja Presiden** (Sub Usecase: *Janji, Arahan, dan Tindak Lanjut Presiden per Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Janji, Arahan, dan Tindak Lanjut Presiden per Wilayah |
| **Publisher** | Biro Pers, Media, dan Informasi Sekretariat Presiden (`setpres`) |
| **Source Name** | `statistik_kunjungan_presiden` |
| **Tipe Akses** | Web Scraping Arsip Siaran Pers & Dokumentasi Resmi Kunjungan |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://id.wikipedia.org/wiki/Daftar_kunjungan_kerja_Prabowo_Subianto` & `https://www.setneg.go.id/baca/index/kunjungan_kenegaraan` |
| **Frekuensi Update** | Bulanan / Per Kunjungan |
| **Target Database** | PostgreSQL (`raw_kunker.raw_setpres_statistik_kunjungan_presiden`) |
| **Target Elasticsearch** | `raw_setpres_statistik_kunjungan_presiden` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Janji, Arahan, dan Tindak Lanjut Presiden per Wilayah.xlsx* (Sheet: *Statistik Kunjungan Wilayah*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `provinsi` | `String` | - | Nama provinsi tempat rangkaian kunjungan kerja Presiden berlangsung. |
| `kabupaten_kota` | `String` | - | Nama kabupaten atau kota lokasi agenda peninjauan/kegiatan kerja Presiden. |
| `frekuensi_kunjungan_total` | `Integer` | Kali | Jumlah akumulasi frekuensi kunjungan Presiden pada wilayah bersangkutan. |
| `kunjungan_terakhir` | `String` (Nullable) | Tanggal | Tanggal atau rentang waktu kunjungan kerja terbaru (misal: `12 Juli 2026`). |
| `agenda_utama` | `String` (Nullable) | - | Uraian fokus kegiatan Presiden (peresmian proyek, panen raya, bansos, rapat kerja). |
| `durasi_kunjungan_hari` | `Integer` (Nullable) | Hari | Estimasi durasi waktu pelaksanaan rangkaian kunjungan kerja di wilayah tersebut. |
| `pejabat_pendamping_utama` | `String` (Nullable) | - | Menteri koordinator, menteri teknis, panglima, atau pimpinan lembaga pendamping. |
| `data_source` | `String` | - | Default: `Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher setpres
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source statistik_kunjungan_presiden --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_setpres_statistik_kunjungan_presiden.py -v
```
