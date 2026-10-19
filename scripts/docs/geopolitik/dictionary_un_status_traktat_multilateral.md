# Data Dictionary: UN Status Traktat Multilateral

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **UN Status Traktat Multilateral** pada usecase **Geopolitik** (Sub Usecase: *Diplomasi Multilateral & Komitmen Internasional*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Diplomasi Multilateral & Komitmen Internasional |
| **Publisher** | United Nations Treaty Collection (UNTC) & Kemenlu RI (`un`) |
| **Source Name** | `status_traktat_multilateral` |
| **Tipe Akses** | Web Scraping / Status of Multilateral Treaties Deposited with the SG |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://treaties.un.org/Pages/ParticipationStatus.aspx?clang=_en` & `https://treaties.un.org/` |
| **Frekuensi Update** | Per Perubahan Status Ratifikasi / Deposit Instrumen |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_un_status_traktat_multilateral`) |
| **Target Elasticsearch** | `raw_un_status_traktat_multilateral` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Data Dictionary - Geopolitik - Diplomasi Multilateral dan Komitmen Internasional.xlsx* (Sheet: *Status Traktat Multilateral*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_traktat` | `String` | kode | Identifier unik traktat multilateral UN Treaty Collection (misal: `UNTC-XXVII-7`). |
| `nama_konvensi_internasional` | `String` | - | Nama lengkap konvensi atau protokol internasional. |
| `organisasi_penyimpan_depository` | `String` | - | Lembaga penyimpan traktat (`Sekjen PBB`, `WIPO`, `IAEA`, dll.). |
| `tanggal_adopsi_dunia` | `Date / String` (Nullable) | tanggal | Waktu traktat diadopsi secara global (format `YYYY-MM-DD`). |
| `status_keikutsertaan_indonesia` | `String` | status | Status keikutsertaan: `Pihak (Diratifikasi)`, `Penandatangan`, `Belum Menjadi Pihak`. |
| `dokumen_pengesahan_uu_ri` | `String` (Nullable) | - | Nomor regulasi ratifikasi Indonesia (misal: `UU No. 16 Tahun 2016`). |
| `tanggal_penyerahan_instrumen` | `Date / String` (Nullable) | tanggal | Waktu deposit instrumen ratifikasi ke Sekjen PBB (format `YYYY-MM-DD`). |
| `catatan_reservasi_deklarasi` | `String` (Nullable) | - | Pernyataan deklarasi interpretatif atau reservasi pasal tertentu oleh RI. |
| `data_source` | `String` | - | Default: `United Nations Treaty Collection (UNTC) & Kemenlu RI`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher un
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source status_traktat_multilateral --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_un_status_traktat_multilateral.py -v
```
