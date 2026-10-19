# Data Dictionary: UN Voting Sidang PBB

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **UN Voting Sidang PBB** pada usecase **Geopolitik** (Sub Usecase: *Diplomasi Multilateral & Komitmen Internasional*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Diplomasi Multilateral & Komitmen Internasional |
| **Publisher** | United Nations Digital Library & PTRI New York (`un`) |
| **Source Name** | `voting_sidang_pbb` |
| **Tipe Akses** | Web Portal Scraping & Digital Library Search |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://digitallibrary.un.org/search?ln=en&cc=Voting+Data` & `https://digitallibrary.un.org/` |
| **Frekuensi Update** | Per Sidang Voting Majelis Umum PBB & Dewan Keamanan PBB |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_un_voting_sidang_pbb`) |
| **Target Elasticsearch** | `raw_un_voting_sidang_pbb` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Data Dictionary - Geopolitik - Diplomasi Multilateral dan Komitmen Internasional.xlsx* (Sheet: *Voting Rekor Sidang PBB*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `nomor_resolusi` | `String` | kode | Nomor registrasi dokumen resolusi PBB (misal: `A/RES/79/112`). |
| `badan_pbb` | `String` | - | Badan pelaksana voting (`UN General Assembly` / `UN Security Council`). |
| `tanggal_voting` | `Date / String` (Nullable) | tanggal | Waktu pemungutan suara berlangsung (format `YYYY-MM-DD`). |
| `judul_resolusi` | `String` | - | Substansi isu utama yang diputuskan dalam resolusi. |
| `posisi_indonesia` | `String` | posisi | Sikap suara delegasi RI (`In Favor / Setuju`, `Against / Menolak`, `Abstain`). |
| `total_suara_in_favor` | `Integer` | suara | Total negara anggota yang mendukung resolusi. |
| `total_suara_against` | `Integer` | suara | Total negara anggota yang menolak resolusi. |
| `total_abstain` | `Integer` | suara | Total negara anggota yang menyatakan abstain. |
| `posisi_negara_mitra_utama` | `String` (Nullable) | - | Perbandingan posisi suara mitra strategis (ASEAN, Non-Blok, P5, dll.). |
| `data_source` | `String` | - | Default: `United Nations Digital Library & PTRI New York`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher un
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source voting_sidang_pbb --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_un_voting_sidang_pbb.py -v
```
