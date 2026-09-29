# Data Dictionary: Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `Ketenagakerjaan`
- Source: `Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI)`
- Publisher: Mahkamah Agung RI
- Data access: `pdf`
- Update frequency: Daily
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=sXmLNM&nav=MTVfezlBMUQyMjZELTM5N0EtNDkyNC1CQTVGLTc3NzE4QjQ3QUZCN30)
- Target module: `ingestion/usecases/ketenagakerjaan/direktori_putusan_perkara_pengadilan_hubungan/models.py`

## Fields

| Label | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|
| GAP: tidak ada breakdown wilayah (provinsi/kab-kota) maupun sektor - hanya agregat Pusat vs Daerah; versi lama per-provinsi (old.satudata.kemnaker.go.id) sudah tidak aktif; Perselisihan yang Ditangani dan Diselesaikan oleh Mediator | - | - | - |
| Download manual dari portal satudata kemnaker | - | - | - |
| Tersedia data per kabupaten kota, perlu validasi apakah semua kabkota ada, Kompilasi laporan resmi kejadian pemogokan kerja, perusahaan terdampak, dan buruh terlibat yang dihimpun dinas ketenagakerjaan daerah melalui portal Satu Data Indonesia. | - | - | - |
| Last update Juli 2026, data Penyampaian Pendapat bisa didapatkan dari POLDA (Jumlah kasus, pokok tuntutan, status/hasil kegiatan). Tidak ada data per-sektor dan per-perusahaan | - | - | - |
| Ditetapkan secara resmi melalui Surat Keputusan Gubernur berdasarkan formula regulasi pengupahan. Last Update 2020 | - | - | - |
| GAP UMK: tidak ada agregator nasional resmi tunggal untuk UMK - setiap provinsi menerbitkan SK Gubernur sendiri, format & waktu rilis TIDAK seragam | - | - | - |
| SK Gubernur Aceh Nomor 500.15.14.1/1495/2025 -> tidak ditemukan open source untuk dokumen tsb | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| DKI Jakarta adalah provinsi kota tunggal - tidak ada breakdown kab/kota yang berlaku. | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda | - | - | - |
| survei KHL tahunan resmi itu dihentikan sejak PP 78/2015 tentang Pengupahan, yang mengubah formula UMP dari berbasis KHL menjadi inflasi + pertumbuhan ekonomi. dari pemberitaan 2025-2026 (Tempo, Antara, Liputan6), Kemnaker ternyata menghidupkan kembali survei KHL sebagai basis penetapan UMP 2026 | - | - | - |
| GAP TERSISA: KHM/KHL tetap hanya level provinsi & tahunan; IHK dari siaran pers bersifat nasional (bukan per kota/provinsi) sehingga untuk breakdown wilayah tetap perlu tabel dinamis #2. | - | - | - |
| GAP TERSISA: KHM/KHL tetap hanya level provinsi & tahunan; IHK dari siaran pers bersifat nasional (bukan per kota/provinsi) sehingga untuk breakdown wilayah tetap perlu tabel dinamis #2. | - | - | - |
| GAP TERSISA: KHM/KHL tetap hanya level provinsi & tahunan; IHK dari siaran pers bersifat nasional (bukan per kota/provinsi) sehingga untuk breakdown wilayah tetap perlu tabel dinamis #2. | - | - | - |
| - Download manual dari portal satudata kemnaker - Tidak tersedia informasi dalam satuan wilayah | - | - | - |
| Need Account, Laporan sistem pengawasan kepatuhan norma pengupahan dan norma kerja daring (Norma 100) Ditjen Binwasnaker Kemnaker RI. | - | - | - |
| DATA (>4 tahun) - Required data tidak ditemukan. Perlu Integrasi Sistem KL ke Ditjen Binwasnaker & K3, | - | - | - |
| Dibandingkan Required Data: - Jumlah perusahaan diperiksa: TIDAK ADA - Jumlah/proporsi patuh: TIDAK ADA ('terlapor WLKP' bukan ukuran patuh terhadap ketentuan pengupahan) - Jumlah/jenis pelanggaran: TIDAK ADA - Hasil pemeriksaan: TIDAK ADA - Ketentuan dilanggar: TIDAK ADA - Tindak lanjut/sanksi: TIDAK ADA - Wilayah: ADA (breakdown 38 provinsi) - Sektor: TIDAK ADA - Periode: ADA (bulanan/kumulatif, data terakhir Agustus 2026) Kesimpulan: hanya 2 dari 9 required data yang tersedia (wilayah, periode). Source ini mengukur kepatuhan LAPOR ke WLKP, bukan kepatuhan terhadap ketentuan pengupahan/norma ketenagakerjaan seperti diminta requirement. | - | - | - |
| Dibandingkan Required Data: - Jumlah perusahaan diperiksa: TIDAK ADA - Jumlah/proporsi patuh: TIDAK ADA (ini jumlah lapor PP, bukan patuh ketentuan pengupahan) - Jumlah/jenis pelanggaran: TIDAK ADA - Hasil pemeriksaan: TIDAK ADA - Ketentuan dilanggar: TIDAK ADA - Tindak lanjut/sanksi: TIDAK ADA - Wilayah: ADA (Tabel 1: 37 provinsi x skala perusahaan) - Sektor: ADA (Tabel 2: 37 provinsi x 18 kategori Lapangan Usaha/KBLI) - Periode: ADA (bulanan kumulatif, data Januari-Juli 2026) Kesimpulan: wilayah, sektor, dan periode tersedia (3 dari 9). Source ini mengukur kepatuhan MELAPORKAN dokumen PP, bukan kepatuhan terhadap ketentuan pengupahan/norma ketenagakerjaan seperti diminta requirement - tetap tidak ada data pemeriksaan/pelanggaran/sanksi. | - | - | - |
| Dibandingkan Required Data: - Jumlah perusahaan diperiksa: TIDAK ADA - Jumlah/proporsi patuh: TIDAK ADA (ini jumlah lapor Struktur Skala Upah, bukan patuh ketentuan pengupahan) - Jumlah/jenis pelanggaran: TIDAK ADA - Hasil pemeriksaan: TIDAK ADA - Ketentuan dilanggar: TIDAK ADA - Tindak lanjut/sanksi: TIDAK ADA - Wilayah: ADA (Tabel 1: 38 provinsi x skala perusahaan) - Sektor: ADA (Tabel 2: 38 provinsi x 18 kategori Lapangan Usaha/KBLI) - Periode: ADA (bulanan kumulatif, data Januari-Juli 2026) Kesimpulan: wilayah, sektor, dan periode tersedia (3 dari 9). Source ini mengukur kepatuhan MELAPORKAN dokumen Struktur Skala Upah, bukan kepatuhan terhadap ketentuan pengupahan secara substantif - tetap tidak ada data pemeriksaan/pelanggaran/sanksi. | - | - | - |
| Dibandingkan Required Data: - Jumlah perusahaan diperiksa: TIDAK ADA - Jumlah/proporsi patuh: TIDAK ADA (ini jumlah lapor PKB, bukan patuh ketentuan pengupahan) - Jumlah/jenis pelanggaran: TIDAK ADA - Hasil pemeriksaan: TIDAK ADA - Ketentuan dilanggar: TIDAK ADA - Tindak lanjut/sanksi: TIDAK ADA - Wilayah: ADA (Tabel 1: 37 provinsi x skala perusahaan) - Sektor: ADA (Tabel 2: 37 provinsi x 18 kategori Lapangan Usaha/KBLI) - Periode: ADA (bulanan kumulatif, data Januari-Juli 2026) Kesimpulan: wilayah, sektor, dan periode tersedia (3 dari 9). Source ini mengukur kepatuhan MELAPORKAN dokumen PKB (hasil perundingan serikat pekerja-pengusaha), bukan kepatuhan terhadap ketentuan pengupahan/norma ketenagakerjaan - tetap tidak ada data pemeriksaan/pelanggaran/sanksi. | - | - | - |
| SUMBER NON-RESMI - wajib diverifikasi silang dengan data resmi sebelum ditampilkan sebagai fakta ke pimpinan; risiko perubahan struktur halaman | - | - | - |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class DirektoriPutusanPerkaraPengadilanHubunganRecord(BaseModel):
    gap_tidak_ada_breakdown_wilayah_maupun_sektor: str | None = Field(default=None, alias="GAP: tidak ada breakdown wilayah (provinsi/kab-kota) maupun sektor - hanya agregat Pusat vs Daerah; versi lama per-provinsi (old.satudata.kemnaker.go.id) sudah tidak aktif; Perselisihan yang Ditangani dan Diselesaikan oleh Mediator")
    download_manual_dari_portal_satudata_kemnaker: str | None = Field(default=None, alias="Download manual dari portal satudata kemnaker")
    tersedia_data_per_kabupaten_kota_perlu_validasi: str | None = Field(default=None, alias="Tersedia data per kabupaten kota, perlu validasi apakah semua kabkota ada, Kompilasi laporan resmi kejadian pemogokan kerja, perusahaan terdampak, dan buruh terlibat yang dihimpun dinas ketenagakerjaan daerah melalui portal Satu Data Indonesia.")
    last_update_juli_2026_data_penyampaian_pendapat: str | None = Field(default=None, alias="Last update Juli 2026, data Penyampaian Pendapat bisa didapatkan dari POLDA (Jumlah kasus, pokok tuntutan, status/hasil kegiatan). Tidak ada data per-sektor dan per-perusahaan")
    ditetapkan_secara_resmi_melalui_surat_keputusan: str | None = Field(default=None, alias="Ditetapkan secara resmi melalui Surat Keputusan Gubernur berdasarkan formula regulasi pengupahan. Last Update 2020")
    gap_umk_tidak_ada_agregator_nasional_resmi: str | None = Field(default=None, alias="GAP UMK: tidak ada agregator nasional resmi tunggal untuk UMK - setiap provinsi menerbitkan SK Gubernur sendiri, format & waktu rilis TIDAK seragam")
    sk_gubernur_aceh_nomor_500_15_14_1_1495_2025: str | None = Field(default=None, alias="SK Gubernur Aceh Nomor 500.15.14.1/1495/2025 -> tidak ditemukan open source untuk dokumen tsb")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    dki_jakarta_adalah_provinsi_kota_tunggal_tidak: str | None = Field(default=None, alias="DKI Jakarta adalah provinsi kota tunggal - tidak ada breakdown kab/kota yang berlaku.")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    source_dari_keputusan_gubernur_provinsi_title: str | None = Field(default=None, alias="Source dari keputusan gubernur provinsi, title untuk per-tahunnya dapat berbeda")
    survei_khl_tahunan_resmi_itu_dihentikan_sejak_pp: str | None = Field(default=None, alias="survei KHL tahunan resmi itu dihentikan sejak PP 78/2015 tentang Pengupahan, yang mengubah formula UMP dari berbasis KHL menjadi inflasi + pertumbuhan ekonomi. dari pemberitaan 2025-2026 (Tempo, Antara, Liputan6), Kemnaker ternyata menghidupkan kembali survei KHL sebagai basis penetapan UMP 2026")
    gap_tersisa_khm_khl_tetap_hanya_level_provinsi: str | None = Field(default=None, alias="GAP TERSISA: KHM/KHL tetap hanya level provinsi & tahunan; IHK dari siaran pers bersifat nasional (bukan per kota/provinsi) sehingga untuk breakdown wilayah tetap perlu tabel dinamis #2.")
    gap_tersisa_khm_khl_tetap_hanya_level_provinsi: str | None = Field(default=None, alias="GAP TERSISA: KHM/KHL tetap hanya level provinsi & tahunan; IHK dari siaran pers bersifat nasional (bukan per kota/provinsi) sehingga untuk breakdown wilayah tetap perlu tabel dinamis #2.")
    gap_tersisa_khm_khl_tetap_hanya_level_provinsi: str | None = Field(default=None, alias="GAP TERSISA: KHM/KHL tetap hanya level provinsi & tahunan; IHK dari siaran pers bersifat nasional (bukan per kota/provinsi) sehingga untuk breakdown wilayah tetap perlu tabel dinamis #2.")
    download_manual_dari_portal_satudata_kemnaker: str | None = Field(default=None, alias="- Download manual dari portal satudata kemnaker
- Tidak tersedia informasi dalam satuan wilayah")
    need_account_laporan_sistem_pengawasan_kepatuhan: str | None = Field(default=None, alias="Need Account, Laporan sistem pengawasan kepatuhan norma pengupahan dan norma kerja daring (Norma 100) Ditjen Binwasnaker Kemnaker RI.")
    data_required_data_tidak_ditemukan_perlu: str | None = Field(default=None, alias="DATA (>4 tahun) - Required data tidak ditemukan. Perlu Integrasi Sistem KL ke Ditjen Binwasnaker & K3, ")
    dibandingkan_required_data_jumlah_perusahaan: str | None = Field(default=None, alias="Dibandingkan Required Data:
- Jumlah perusahaan diperiksa: TIDAK ADA
- Jumlah/proporsi patuh: TIDAK ADA ('terlapor WLKP' bukan ukuran patuh terhadap ketentuan pengupahan)
- Jumlah/jenis pelanggaran: TIDAK ADA
- Hasil pemeriksaan: TIDAK ADA
- Ketentuan dilanggar: TIDAK ADA
- Tindak lanjut/sanksi: TIDAK ADA
- Wilayah: ADA (breakdown 38 provinsi)
- Sektor: TIDAK ADA
- Periode: ADA (bulanan/kumulatif, data terakhir Agustus 2026)
Kesimpulan: hanya 2 dari 9 required data yang tersedia (wilayah, periode). Source ini mengukur kepatuhan LAPOR ke WLKP, bukan kepatuhan terhadap ketentuan pengupahan/norma ketenagakerjaan seperti diminta requirement.")
    dibandingkan_required_data_jumlah_perusahaan: str | None = Field(default=None, alias="Dibandingkan Required Data:
- Jumlah perusahaan diperiksa: TIDAK ADA
- Jumlah/proporsi patuh: TIDAK ADA (ini jumlah lapor PP, bukan patuh ketentuan pengupahan)
- Jumlah/jenis pelanggaran: TIDAK ADA
- Hasil pemeriksaan: TIDAK ADA
- Ketentuan dilanggar: TIDAK ADA
- Tindak lanjut/sanksi: TIDAK ADA
- Wilayah: ADA (Tabel 1: 37 provinsi x skala perusahaan)
- Sektor: ADA (Tabel 2: 37 provinsi x 18 kategori Lapangan Usaha/KBLI)
- Periode: ADA (bulanan kumulatif, data Januari-Juli 2026)
Kesimpulan: wilayah, sektor, dan periode tersedia (3 dari 9). Source ini mengukur kepatuhan MELAPORKAN dokumen PP, bukan kepatuhan terhadap ketentuan pengupahan/norma ketenagakerjaan seperti diminta requirement - tetap tidak ada data pemeriksaan/pelanggaran/sanksi.")
    dibandingkan_required_data_jumlah_perusahaan: str | None = Field(default=None, alias="Dibandingkan Required Data:
- Jumlah perusahaan diperiksa: TIDAK ADA
- Jumlah/proporsi patuh: TIDAK ADA (ini jumlah lapor Struktur Skala Upah, bukan patuh ketentuan pengupahan)
- Jumlah/jenis pelanggaran: TIDAK ADA
- Hasil pemeriksaan: TIDAK ADA
- Ketentuan dilanggar: TIDAK ADA
- Tindak lanjut/sanksi: TIDAK ADA
- Wilayah: ADA (Tabel 1: 38 provinsi x skala perusahaan)
- Sektor: ADA (Tabel 2: 38 provinsi x 18 kategori Lapangan Usaha/KBLI)
- Periode: ADA (bulanan kumulatif, data Januari-Juli 2026)
Kesimpulan: wilayah, sektor, dan periode tersedia (3 dari 9). Source ini mengukur kepatuhan MELAPORKAN dokumen Struktur Skala Upah, bukan kepatuhan terhadap ketentuan pengupahan secara substantif - tetap tidak ada data pemeriksaan/pelanggaran/sanksi.")
    dibandingkan_required_data_jumlah_perusahaan: str | None = Field(default=None, alias="Dibandingkan Required Data:
- Jumlah perusahaan diperiksa: TIDAK ADA
- Jumlah/proporsi patuh: TIDAK ADA (ini jumlah lapor PKB, bukan patuh ketentuan pengupahan)
- Jumlah/jenis pelanggaran: TIDAK ADA
- Hasil pemeriksaan: TIDAK ADA
- Ketentuan dilanggar: TIDAK ADA
- Tindak lanjut/sanksi: TIDAK ADA
- Wilayah: ADA (Tabel 1: 37 provinsi x skala perusahaan)
- Sektor: ADA (Tabel 2: 37 provinsi x 18 kategori Lapangan Usaha/KBLI)
- Periode: ADA (bulanan kumulatif, data Januari-Juli 2026)
Kesimpulan: wilayah, sektor, dan periode tersedia (3 dari 9). Source ini mengukur kepatuhan MELAPORKAN dokumen PKB (hasil perundingan serikat pekerja-pengusaha), bukan kepatuhan terhadap ketentuan pengupahan/norma ketenagakerjaan - tetap tidak ada data pemeriksaan/pelanggaran/sanksi.")
    sumber_non_resmi_wajib_diverifikasi_silang: str | None = Field(default=None, alias="SUMBER NON-RESMI - wajib diverifikasi silang dengan data resmi sebelum ditampilkan sebagai fakta ke pimpinan; risiko perubahan struktur halaman")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
