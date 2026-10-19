# Data Dictionary: BPS Profil Sosioekonomi Wilayah

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **BPS Profil Sosioekonomi Wilayah** pada usecase **Kunjungan Presiden** (Sub Usecase: *Peta dan Profil Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Peta dan Profil Wilayah |
| **Publisher** | Badan Pusat Statistik (BPS) (`bps`) |
| **Source Name** | `profil_sosioekonomi` |
| **Tipe Akses** | REST API (JSON) BPS Web API & Interoperabilitas SIMDASI |
| **Kebutuhan Registrasi / Login** | **Perlu Registrasi / API Key Gratis (`App ID`)** |
| **Endpoint Live Sumber** | `https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/26/key/WebAPI_KEY/` |
| **Dokumentasi API** | `https://webapi.bps.go.id/developer/` |
| **Frekuensi Update** | Tahunan / Semesteran |
| **Target Database** | PostgreSQL (`raw_kunker.raw_bps_profil_sosioekonomi`) |
| **Target Elasticsearch** | `raw_bps_profil_sosioekonomi` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Peta dan Profil Wilayah.xlsx* (Sheet: *Profil Sosio-Ekonomi Wilayah*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `kode_wilayah_kemendagri` | `String` | kode | Kode wilayah administrasi Kemendagri (contoh: `33.02`, `32.04`). |
| `provinsi` | `String` | - | Nama provinsi (contoh: `Jawa Tengah`, `Jawa Barat`). |
| `kabupaten_kota` | `String` | - | Nama kabupaten/kota sasaran kunjungan kerja. |
| `jumlah_penduduk_jiwa` | `Integer` | jiwa | Jumlah penduduk total semesteran. |
| `kepadatan_penduduk_km2` | `Float` | jiwa/km2 | Kepadatan penduduk per kilometer persegi. |
| `persentase_penduduk_miskin` | `Float` | % | Persentase penduduk miskin daerah (%). |
| `tingkat_pengangguran_terbuka_tpt` | `Float` | % | Tingkat Pengangguran Terbuka (TPT) daerah (%). |
| `indeks_pembangunan_manusia_ipm` | `Float` | skor | Indeks Pembangunan Manusia (IPM) daerah (skor 0-100). |
| `pertumbuhan_ekonomi_pdrb_pct` | `Float` | % | Laju pertumbuhan PDRB riil tahunan (%). |
| `pdrb_harga_berlaku_juta_rp` | `Float` | Juta Rp | Nominal PDRB Atas Dasar Harga Berlaku (Juta Rupiah). |
| `data_source` | `String` | - | Default: `Badan Pusat Statistik (BPS)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher bps
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source profil_sosioekonomi --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_bps_profil_sosioekonomi.py -v
```
