# Data Dictionary: Kemenkes SATUSEHAT Cek Kesehatan Gratis (CKG)

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Kementerian Kesehatan RI SATUSEHAT Cek Kesehatan Gratis (CKG)** pada usecase **Kunjungan Presiden** (Sub Usecase: *Peta dan Profil Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Peta dan Profil Wilayah |
| **Publisher** | Kementerian Kesehatan RI (SATUSEHAT & Ditjen Kesmas) (`kemenkes`) |
| **Source Name** | `satusehat_ckg` |
| **Tipe Akses** | REST API OAuth2 FHIR SATUSEHAT Platform |
| **Kebutuhan Registrasi / Login** | **Khusus Institusi Fasyankes / Pemerintah** |
| **Endpoint Live Sumber** | `https://satusehat.kemkes.go.id/platform/fhir-id/v1/Observation` |
| **Portal Layanan** | `https://ayockg.kemkes.go.id/` |
| **Frekuensi Update** | Harian |
| **Target Database** | PostgreSQL (`raw_kunker.raw_kemenkes_satusehat_ckg`) |
| **Target Elasticsearch** | `raw_kemenkes_satusehat_ckg` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Peta dan Profil Wilayah.xlsx* (Sheet: *Cek Kesehatan Gratis CKG*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_fasyankes` | `String` | kode | Kode registrasi fasyankes SATUSEHAT Kemenkes (contoh: `P33020101`). |
| `nama_puskesmas_klinik` | `String` | - | Nama fasilitas pelayanan kesehatan pelaksana skrining CKG. |
| `provinsi` | `String` | - | Provinsi lokasi fasyankes. |
| `kabupaten_kota` | `String` | - | Kabupaten atau kota lokasi fasyankes. |
| `jumlah_skrining_balita` | `Integer` | jiwa | Jumlah balita yang telah diskrining tumbuh kembang. |
| `jumlah_skrining_dewasa` | `Integer` | jiwa | Jumlah usia produktif diskrining penyakit tidak menular (PTM). |
| `jumlah_skrining_lansia` | `Integer` | jiwa | Jumlah warga lansia diskrining kesehatan geriatri. |
| `kasus_terindikasi_stunting` | `Integer` | kasus | Balita terindikasi stunting / wasting. |
| `kasus_dirujuk_ke_rs` | `Integer` | kasus | Pasien yang memerlukan rujukan fasyankes lanjutan. |
| `data_source` | `String` | - | Default: `Kementerian Kesehatan RI (SATUSEHAT & Ditjen Kesmas)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher kemenkes
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source satusehat_ckg --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_kemenkes_satusehat_ckg.py -v
```
