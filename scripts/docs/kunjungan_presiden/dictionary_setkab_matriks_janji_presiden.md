# Data Dictionary: Setkab Matriks Janji & Arahan Presiden per Wilayah

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Setkab Matriks Janji & Arahan Presiden** pada usecase **Kunjungan Kerja Presiden** (Sub Usecase: *Janji, Arahan, dan Tindak Lanjut Presiden per Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Janji, Arahan, dan Tindak Lanjut Presiden per Wilayah |
| **Publisher** | Deputi Bidang Dukungan Kerja Kabinet Sekretariat Kabinet (`setkab`) |
| **Source Name** | `matriks_janji_presiden` |
| **Tipe Akses** | Web Scraping Portal Berita Arahan & Dokumen Tindak Lanjut Setkab RI |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://setkab.go.id/` |
| **Frekuensi Update** | Bulanan / Per Arahan Kerja Baru |
| **Target Database** | PostgreSQL (`raw_kunker.raw_setkab_matriks_janji_presiden`) |
| **Target Elasticsearch** | `raw_setkab_matriks_janji_presiden` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Janji, Arahan, dan Tindak Lanjut Presiden per Wilayah.xlsx* (Sheet: *Matriks Janji dan Arahan*):

| Nama Kolom | Tipe Data | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- |
| `id_komitmen` | `String` | Identifier resmi komitmen janji/arahan Presiden (misal: `JNJ-2026-001`). |
| `program_strategis` | `String` | Rumpun program atau sektor strategis prioritas Presiden (TPST, KDMP, Perumahan MBR, dsb). |
| `substansi_komitmen` | `String` | Uraian isi komitmen, target kuantitatif, atau arahan kerja spesifik Presiden. |
| `tanggal_penyampaian` | `String` (Nullable) | Tanggal penyampaian komitmen/arahan (format: `YYYY-MM-DD` atau deskriptif). |
| `forum_agenda` | `String` (Nullable) | Konteks seremonial kunjungan, rapat terbatas, atau forum kenegaraan saat arahan disampaikan. |
| `provinsi` | `String` (Nullable) | Provinsi sasaran program atau lokasi kunjungan kerja Presiden. |
| `kabupaten_kota` | `String` (Nullable) | Kabupaten/Kota target penerima manfaat komitmen. |
| `desa_lokasi` | `String` (Nullable) | Lokasi titik desa/kawasan fisik peninjauan proyek. |
| `kl_penanggung_jawab` | `String` (Nullable) | Kementerian / Lembaga teknis pengampu eksekusi program. |
| `status_pemenuhan` | `String` | Status pelaksanaan komitmen (`Selesai`, `On Progress`, `Terkendala`). Default: `On Progress`. |
| `catatan_progres_sekdukkab` | `String` (Nullable) | Catatan perkembangan monitoring Tim Dukungan Kerja Kabinet (Sekdukkab). |
| `koordinasi_kemenko` | `String` (Nullable) | Kementerian Koordinator pembina penyelesaian komitmen. |
| `data_source` | `String` | Default: `Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher setkab
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source matriks_janji_presiden --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_setkab_matriks_janji_presiden.py -v
```
