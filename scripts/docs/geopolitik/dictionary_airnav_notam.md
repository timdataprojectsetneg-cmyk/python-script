# Data Dictionary: AirNav NOTAM & Kesiapan Evakuasi WNI

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **AirNav NOTAM & Kesiapan Evakuasi WNI** pada usecase **Geopolitik** (Sub Usecase: *Pelindungan WNI di Luar Negeri*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Geopolitik (`geopolitik`) |
| **Sub Usecase** | Pelindungan WNI di Luar Negeri |
| **Publisher** | AirNav Indonesia (Perum LPPNPI) & Kementerian Luar Negeri RI (`airnav`) |
| **Source Name** | `notam` |
| **Tipe Akses** | Web Portal & Sistem Informasi Aeronautika (PIA) / Rencana Kontinjensi Evakuasi WNI |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://pia.airnavindonesia.co.id/` & `https://notams.aim.faa.gov/notamSearch/` |
| **Frekuensi Update** | Harian / Saat Situasi Krisis Geopolitik Memburuk |
| **Target Database** | PostgreSQL (`raw_geopolitik.raw_airnav_notam`) |
| **Target Elasticsearch** | `raw_airnav_notam` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Pelindungan WNI di Luar Negeri.xlsx* (Sheet: *Kesiapan Evakuasi dan NOTAM*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_wilayah` | `String` | kode | Identifier unik rencana kontinjensi wilayah (misal: `EVAC-2026-ME-01`). |
| `negara` | `String` | - | Negara lokasi kontinjensi krisis, eskalasi konflik, atau penutupan wilayah udara. |
| `kawasan` | `String` | - | Kawasan geopolitik (misal: `Timur Tengah`, `Afrika Utara`, `Eropa Timur`). |
| `status_siaga_evakuasi` | `String` | level | Tingkat kesiagaan evakuasi: `Siaga I` (Evakuasi Penuh), `Siaga II`, `Siaga III`. |
| `estimasi_wni_terdampak` | `Integer` | jiwa | Jumlah WNI yang berada dalam zona bahaya atau terdata pada perwakilan RI. |
| `jalur_evakuasi_utama` | `String` (Nullable) | - | Moda dan rute evakuasi (Jalur Udara, Koridor Darat ke Perbatasan, Konvoi Laut). |
| `titik_kumpul_safe_haven` | `String` (Nullable) | - | Lokasi aman penampungan WNI sebelum dipulangkan (KBRI, Wisma Duta, Pangkalan). |
| `status_ruang_udara_notam` | `String` | - | Status ruang udara penerbangan berdasarkan NOTAM (`Open`, `Restricted`, `Closed`). |
| `kesiapan_bandara_pelabuhan` | `String` (Nullable) | - | Status dan kondisi operasional fasilitas keberangkatan evakuasi. |
| `koordinasi_satgas_tni_kemlu` | `String` (Nullable) | - | Kesiapan koordinasi armada KRI / pesawat angkut TNI AU dan tim evakuasi Kemlu. |
| `data_source` | `String` | - | Default: `AirNav Indonesia & Kementerian Luar Negeri RI (Satgas Evakuasi WNI)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher airnav
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase geopolitik --source notam --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_airnav_notam.py -v
```
