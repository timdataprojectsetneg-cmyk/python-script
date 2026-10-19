# Data Dictionary: Kemendesa Indeks Desa Membangun (IDM)

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Kemendesa Indeks Desa Membangun (IDM)** pada usecase **Kunjungan Kerja Presiden** (Sub Usecase: *Konteks Sosial dan Kelembagaan Wilayah*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Konteks Sosial dan Kelembagaan Wilayah |
| **Publisher** | Kementerian Desa, Pembangunan Daerah Tertinggal, dan Transmigrasi RI (`kemendesa`) |
| **Source Name** | `idm` |
| **Tipe Akses** | REST JSON API Publik (Kemendesa IDM Open API) |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live** | `https://idm.kemendesa.go.id/open/api` |
| **Frekuensi Update** | Tahunan |
| **Target Database** | PostgreSQL (`raw_kunker.raw_kemendesa_idm`) |
| **Target Elasticsearch** | `raw_kemendesa_idm` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Alpha Data Dictionary - Konteks Sosial dan Kelembagaan Wilayah.xlsx* (Sheet: *Indeks Desa Membangun IDM*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_kabupaten` | `String` (Nullable) | Kode | Kode wilayah administrasi kabupaten/kota (misal: `3302`). |
| `provinsi` | `String` | - | Nama provinsi wilayah administrasi (misal: *Jawa Tengah*). |
| `kabupaten_kota` | `String` | - | Nama kabupaten/kota wilayah administrasi (misal: *Kabupaten Banyumas*). |
| `total_desa` | `Integer` | desa | Total jumlah desa di wilayah kabupaten/kota. |
| `total_kecamatan` | `Integer` (Nullable) | kecamatan | Total jumlah kecamatan di wilayah kabupaten/kota. |
| `desa_mandiri` | `Integer` | desa | Jumlah/estimasi desa berstatus Mandiri (skor IDM $\ge$ 0.8155). |
| `desa_maju` | `Integer` | desa | Jumlah/estimasi desa berstatus Maju (0.7072 $\le$ skor < 0.8155). |
| `desa_berkembang` | `Integer` | desa | Jumlah/estimasi desa berstatus Berkembang (0.5989 $\le$ skor < 0.7072). |
| `desa_tertinggal` | `Integer` | desa | Jumlah/estimasi desa berstatus Tertinggal (0.4907 $\le$ skor < 0.5989). |
| `desa_sangat_tertinggal` | `Integer` | desa | Jumlah/estimasi desa berstatus Sangat Tertinggal (skor < 0.4907). |
| `indeks_ketahanan_sosial` | `Float` (Nullable) | skor | Rata-rata skor ketahanan sosial desa (IKS: kesehatan, pendidikan, modal sosial, permukiman). |
| `indeks_ketahanan_ekonomi` | `Float` (Nullable) | skor | Rata-rata skor ketahanan ekonomi desa (IKE: perdagangan, distribusi, kredit, lembaga ekonomi). |
| `indeks_ketahanan_lingkungan` | `Float` (Nullable) | skor | Rata-rata skor ketahanan ekologi/lingkungan desa (IKL: kualitas lingkungan, tanggap bencana). |
| `skor_idm` | `Float` (Nullable) | skor | Rata-rata komposit IDM = (IKS + IKE + IKL) / 3. |
| `status_idm` | `String` | - | Klasifikasi status IDM: `MANDIRI`, `MAJU`, `BERKEMBANG`, `TERTINGGAL`, `SANGAT TERTINGGAL`. |
| `tahun` | `Integer` | tahun | Tahun penilaian IDM (default: 2024). |
| `data_source` | `String` | - | Sumber data resmi: `Kementerian Desa PDTT - IDM Open API`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher kemendesa
```

### Eksekusi Live Ingestion
```powershell
# Ekstrak 5 kabupaten prioritas
python run_ingestion.py run --usecase kunjungan_presiden --source idm --limit 5

# Ekstrak seluruh kabupaten di provinsi tertentu
python run_ingestion.py run --usecase kunjungan_presiden --source idm
```

### Menjalankan Unit Test
```powershell
pytest tests/unit/test_kemendesa_idm.py -v
```
