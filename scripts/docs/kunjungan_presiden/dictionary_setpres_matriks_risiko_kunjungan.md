# Data Dictionary: Setpres Matriks Risiko Kunjungan

Dokumen ini mendefinisikan skema data, arsitektur ekstraksi, normalisasi, dan integrasi untuk modul **Setpres Matriks Risiko Kunjungan** pada usecase **Kunjungan Presiden** (Sub Usecase: *Kesiapan Kunjungan*).

---

## 1. Metadata Sumber Data

| Atribut | Nilai |
| :--- | :--- |
| **Usecase** | Kunjungan Presiden (`kunjungan_presiden`) |
| **Sub Usecase** | Kesiapan Kunjungan |
| **Publisher** | Sekretariat Presiden RI (Biro Protokol) & Paspampres (`setpres`) |
| **Source Name** | `matriks_risiko_kunjungan` |
| **Tipe Akses** | Warta Kunjungan Kenegaraan & Regulasi Pengamanan VVIP (UU 9/2010 Keprotokolan) |
| **Kebutuhan Registrasi / Login** | **Publik Terbuka (Tanpa Akun / Login / API Key)** |
| **Endpoint Live Sumber** | `https://www.setneg.go.id/baca/index/kunjungan_kenegaraan` & `https://www.peraturan.go.id/files/uu9-2010bt.pdf` |
| **Frekuensi Update** | Per Agenda Kunjungan Kerja Lapangan (Kunker) |
| **Target Database** | PostgreSQL (`raw_kunker.raw_setpres_matriks_risiko_kunjungan`) |
| **Target Elasticsearch** | `raw_setpres_matriks_risiko_kunjungan` |

---

## 2. Skema Data (Data Dictionary)

Sesuai dengan spesifikasi KAK dan lembar *Kesiapan Kunjungan.xlsx* (Sheet: *Matriks Risiko Kesiapan*):

| Nama Kolom | Tipe Data | Satuan | Keterangan & Aturan Transformasi |
| :--- | :--- | :--- | :--- |
| `id_risiko` | `String` | kode | Identifier unik analisis risiko kunker (misal: `RSK-2026-01`). |
| `kategori_risiko` | `String` | - | Kategori risiko (`Protokoler`, `Medis`, `Cuaca`, `Kerawanan Massa`, `Aksesibilitas`). |
| `deskripsi_ancaman` | `String` | - | Potensi kendala atau gangguan yang teridentifikasi di lokasi kunjungan. |
| `tingkat_probabilitas` | `String` | level | Peluang terjadinya kendala: `Tinggi`, `Sedang`, `Rendah`. |
| `tingkat_dampak` | `String` | level | Dampak kelancaran acara kepresidenan: `Kritis`, `Signifikan`, `Minor`. |
| `rencana_mitigasi` | `String` (Nullable) | - | Langkah antisipasi dan skenario cadangan (*Plan B*). |
| `penanggung_jawab_pic` | `String` (Nullable) | - | Satgas pengampu mitigasi (Paspampres, Protokol Setpres, Dinkes, Kodim). |
| `data_source` | `String` | - | Default: `Sekretariat Presiden RI (Biro Protokol) & Paspampres (UU 9/2010 Keprotokolan)`. |

---

## 3. Perintah Eksekusi & Uji Coba

### Dynamic Discovery
```powershell
python run_ingestion.py docs --list sources --publisher setpres
```

### Eksekusi Live Ingestion
```powershell
python run_ingestion.py run --usecase kunjungan_presiden --source matriks_risiko_kunjungan --limit 5
```

### Menjalankan Unit Test Pytest
```powershell
pytest tests/unit/test_setpres_matriks_risiko_kunjungan.py -v
```
