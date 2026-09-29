# Data Dictionary: BPS Inflasi MoM

> Generated from the SharePoint Data Dictionary. Use this as the reference for the Pydantic model in `models.py`.

- Use case: `Ketenagakerjaan`
- Source: `BPS Inflasi MoM`
- Publisher: BPS
- Data access: `api`
- Update frequency: Monthly
- Eligible: `True`
- Data Dictionary file: [Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx](https://telkomind.sharepoint.com/:x:/r/sites/SetnegTeam/Shared%20Documents/Sitroom-2026/PROJECT/DATA/1%20-%20Discover/Data%20Dictionary%20-%20Ketenagakerjaan/Data%20Dictionary%20-%20Ketenagakerjaan%20-%20Hubungan%20Industrial%20dan%20Pengupahan.xlsx?d=w44c390bae78b45c7b1e33bdcfe15c94f&csf=1&web=1&e=zh2F9K&nav=MTVfezczOUE2QjcxLTA5QzktNDNGRS04NUFELUY1RDk3RjRENzIyMX0)
- Target module: `ingestion/usecases/ketenagakerjaan/bps_inflasi_mom/models.py`

## Fields

| Label | Tipe Data | Satuan | Deskripsi |
|---|---|---|---|
| Kota_Inflasi | String | - | Nama kabupaten/kota yang menjadi titik pantau inflasi BPS (mengikuti daftar kota IHK yang dipakai BPS untuk hitung inflasi; bukan seluruh kabupaten/kota di Indonesia, hanya kota-kota sampel yang punya pos pemantauan harga BPS - isinya campuran kategori KAB dan KOTA). |
| Januari s.d. Desember (12 kolom terpisah per bulan) | Decimal | Persen | Persentase perubahan inflasi bulanan (month-to-month/m-to-m) untuk kota tersebut pada bulan yang bersangkutan, dihitung dari perubahan Indeks Harga Konsumen (IHK) bulan berjalan dibanding bulan sebelumnya. Tanda "-" berarti data bulan tersebut belum dirilis BPS. |
| Tahunan | Decimal | Persen | Akumulasi inflasi tahun kalender (year-to-date, dari Januari s.d. bulan terakhir yang tersedia) - BUKAN inflasi year-on-year (data y-o-y ada di sheet terpisah "BPS Inflasi YOY"). Perlu dikonfirmasi ke definisi asli BPS untuk memastikan. |
| Sample Data: | - | - | - |
| Kota Inflasi | - | - | - |
| KAB ACEH TENGAH | -0,01 | -0,48 | -0,56 |
| KOTA MEULABOH | -0,45 | 0,48 | 0,10 |
| KAB ACEH TAMIANG | 0,26 | -1,64 | 0,46 |
| KOTA BANDA ACEH | -0,81 | 0,42 | 0,12 |
| KOTA LHOKSEUMAWE | 0,86 | -0,05 | 0,11 |
| KAB LABUHANBATU | -0,83 | 0,79 | -0,57 |
| KAB KARO | 0,03 | -0,02 | -0,38 |
| KAB DELI SERDANG | -1,30 | -0,08 | -0,26 |
| KOTA SIBOLGA | -0,26 | 0,66 | -0,20 |
| KOTA PEMATANG SIANTAR | -0,11 | 0,57 | -0,02 |
| KOTA MEDAN | -0,62 | 0,33 | -0,01 |
| KOTA PADANGSIDIMPUAN | -0,32 | -0,01 | -0,01 |
| KOTA GUNUNGSITOLI | -2,37 | -0,87 | -0,43 |
| KAB DHARMASRAYA | -0,92 | 0,85 | 0,44 |
| KAB PASAMAN BARAT | -1,84 | -0,13 | -0,05 |
| KOTA PADANG | -1,02 | 0,32 | -0,02 |
| KOTA BUKITTINGGI | -0,73 | 0,50 | 0,16 |
| TEMBILAHAN | -0,24 | 0,94 | 0,17 |
| KAB KAMPAR | -0,66 | 0,32 | -0,23 |
| KOTA PEKANBARU | -0,35 | 0,24 | -0,19 |
| KOTA DUMAI | -0,42 | 0,50 | -0,28 |
| KAB KERINCI | -1,31 | 1,07 | 1,28 |
| BUNGO | -0,17 | 0,93 | 0,22 |
| KOTA JAMBI | -0,25 | 0,38 | -0,22 |
| KAB OGAN KOMERING ILIR | 0,08 | 0,60 | 0,36 |
| KAB MUARA ENIM | 0,06 | 0,64 | 0,24 |
| KOTA PALEMBANG | 0,05 | 0,58 | 0,28 |
| KOTA LUBUKLINGGAU | 0,03 | 0,41 | 0,27 |
| KAB MUKO MUKO | -0,87 | 0,85 | 0,81 |
| KOTA BENGKULU | -0,72 | 0,60 | 0,10 |
| KAB LAMPUNG TIMUR | -0,40 | 0,15 | 0,04 |
| KAB MESUJI | -0,51 | 0,33 | 0,80 |
| KOTA BANDAR LAMPUNG | 0,18 | 0,44 | 0,20 |
| KOTA METRO | -0,34 | 0,48 | 0,17 |
| TANJUNG PANDAN | 0,81 | -1,56 | 0,18 |
| KAB BANGKA BARAT | 0,36 | -0,77 | 0,92 |
| KAB BELITUNG TIMUR | 0,03 | -0,01 | 0,31 |
| KOTA PANGKAL PINANG | 0,11 | -0,44 | 0,21 |
| KAB KARIMUN | -0,67 | 0,01 | 0,56 |
| KOTA BATAM | -0,04 | 0,40 | 0,11 |
| KOTA TANJUNG PINANG | -0,06 | 0,99 | -0,37 |
| DKI JAKARTA | -0,23 | 0,63 | 0,51 |
| KAB BANDUNG | -0,15 | 0,96 | 0,59 |
| KAB MAJALENGKA | -0,11 | 0,85 | 0,62 |
| KAB SUBANG | -0,21 | 0,88 | 0,67 |
| KOTA BOGOR | -0,21 | 0,91 | 0,52 |
| KOTA SUKABUMI | -0,03 | 0,75 | 0,46 |
| KOTA BANDUNG | -0,09 | 0,65 | 0,43 |
| KOTA CIREBON | -0,44 | 0,80 | 0,68 |
| KOTA BEKASI | 0,07 | 0,83 | 0,39 |
| KOTA DEPOK | -0,16 | 0,65 | 0,63 |
| KOTA TASIKMALAYA | -0,05 | 0,97 | 0,44 |
| CILACAP | -0,42 | 0,80 | 0,70 |
| PURWOKERTO | -0,36 | 0,78 | 0,68 |
| KAB WONOSOBO | -0,51 | 0,76 | 0,92 |
| KAB WONOGIRI | -0,52 | 0,79 | 0,87 |
| KAB REMBANG | -0,29 | 0,83 | 0,53 |
| KUDUS | -0,26 | 0,74 | 0,47 |
| KOTA SURAKARTA | -0,38 | 0,90 | 0,48 |
| KOTA SEMARANG | -0,25 | 0,67 | 0,37 |
| KOTA TEGAL | -0,24 | 0,86 | 0,54 |
| KAB GUNUNGKIDUL | -0,17 | 0,66 | 0,55 |
| KOTA YOGYAKARTA | -0,14 | 0,72 | 0,33 |
| KAB TULUNGAGUNG | -0,18 | 1,03 | 0,47 |
| JEMBER | -0,29 | 1,14 | 0,65 |
| BANYUWANGI | -0,21 | 0,94 | 0,37 |
| KAB BOJONEGORO | -0,33 | 0,91 | 0,65 |
| KAB GRESIK | -0,45 | 0,76 | 0,98 |
| SUMENEP | 0,34 | 1,08 | 0,89 |
| KOTA KEDIRI | -0,37 | 0,87 | 0,41 |
| KOTA MALANG | -0,10 | 0,74 | 0,34 |
| KOTA PROBOLINGGO | -0,03 | 1,12 | 0,69 |
| KOTA MADIUN | -0,23 | 0,74 | 0,49 |
| KOTA SURABAYA | -0,16 | 0,99 | 0,13 |
| KAB PANDEGLANG | -0,50 | 1,64 | 1,05 |
| KAB LEBAK | -0,34 | 1,52 | 0,62 |
| KOTA TANGERANG | -0,38 | 0,64 | 0,36 |
| KOTA CILEGON | -0,12 | 0,85 | 0,24 |
| KOTA SERANG | -0,16 | 0,73 | 0,31 |
| KAB TABANAN | -0,21 | 0,48 | 0,63 |
| KAB BADUNG | -0,78 | 1,04 | 0,50 |
| SINGARAJA | -0,44 | 0,77 | 0,90 |
| KOTA DENPASAR | -0,13 | 0,57 | 0,42 |
| KAB SUMBAWA | 0,80 | 0,67 | 0,91 |
| KOTA MATARAM | -0,21 | 0,96 | 0,85 |
| KOTA BIMA | 0,61 | 0,91 | 0,29 |
| WAINGAPU | 1,45 | 0,69 | 0,04 |
| KAB TIMOR TENGAH SELATAN | 1,40 | 0,03 | 0,38 |
| MAUMERE | 1,69 | 0,16 | 0,02 |
| KAB NGADA | 0,68 | 0,04 | 0,28 |
| KOTA KUPANG | 0,14 | 0,71 | 0,23 |
| DILI | - | - | - |
| KAB KETAPANG | 0,61 | 0,45 | 0,21 |
| SINTANG | 0,55 | 0,56 | 0,20 |
| KAB KAYONG UTARA | 0,18 | 0,36 | 0,37 |
| KOTA PONTIANAK | 0,07 | 0,57 | 0,17 |
| KOTA SINGKAWANG | 0,11 | 0,53 | 0,55 |
| SAMPIT | 0,41 | 0,61 | 0,43 |
| KAB KAPUAS | 0,47 | 0,67 | 0,89 |
| KAB SUKAMARA | 0,03 | 0,76 | 0,09 |
| KOTA PALANGKA RAYA | 0,36 | 0,17 | 0,44 |
| KAB TANAH LAUT | -0,03 | 1,09 | 1,15 |
| KOTABARU | 0,36 | 0,60 | 0,30 |
| KAB HULU SUNGAI TENGAH | 0,48 | 0,82 | 0,38 |
| TANJUNG | 0,81 | 1,34 | 0,45 |
| KOTA BANJARMASIN | 0,13 | 0,76 | 0,35 |
| KAB BERAU | -0,32 | 0,15 | 0,76 |
| KAB PENAJAM PASER UTARA | 0,05 | 0,89 | 1,09 |
| KOTA BALIKPAPAN | -0,11 | 0,75 | 0,51 |
| KOTA SAMARINDA | 0,26 | 0,56 | 0,86 |
| TANJUNG SELOR | -0,43 | 0,56 | 0,41 |
| KAB NUNUKAN | 0,81 | 0,24 | 0,53 |
| KOTA TARAKAN | -0,15 | 0,58 | 0,63 |
| KAB MINAHASA SELATAN | 0,37 | 1,50 | 0,41 |
| KAB MINAHASA UTARA | 0,94 | 1,45 | -0,35 |
| KOTA MANADO | 0,79 | 0,75 | 0,32 |
| KOTA KOTAMOBAGU | -0,12 | 1,13 | 0,72 |
| LUWUK | 0,07 | 0,92 | 0,37 |
| KAB MOROWALI | -0,13 | 0,57 | 0,62 |
| KAB TOLI TOLI | -0,85 | 1,59 | 0,30 |
| KOTA PALU | 0,24 | 0,66 | 0,33 |
| BULUKUMBA | 0,29 | 0,63 | 0,35 |
| WATAMPONE | 0,91 | 0,48 | 0,80 |
| KAB WAJO | 0,34 | 1,08 | 0,93 |
| KAB SIDENRENG RAPPANG | 1,39 | 0,96 | 0,36 |
| KAB LUWU TIMUR | 0,34 | 0,63 | 1,07 |
| KOTA MAKASSAR | 0,37 | 1,23 | 0,57 |
| KOTA PARE-PARE | 0,47 | 0,65 | 0,49 |
| KOTA PALOPO | 0,37 | 0,49 | 0,20 |
| KAB KONAWE | -0,06 | 0,28 | 1,14 |
| KAB KOLAKA | 1,82 | 1,05 | 0,78 |
| KOTA KENDARI | 0,44 | 0,38 | 0,33 |
| KOTA BAU-BAU | 0,90 | 1,44 | -0,75 |
| KAB GORONTALO | 0,68 | 0,91 | 0,17 |
| KOTA GORONTALO | -0,19 | 0,73 | 0,35 |
| KAB MAJENE | 0,15 | 0,43 | 0,50 |
| MAMUJU | 1,58 | 0,07 | -0,54 |
| KAB MALUKU TENGAH | 1,44 | 1,21 | -1,40 |
| KOTA AMBON | 0,15 | 0,30 | -0,43 |
| KOTA TUAL | 2,35 | -0,72 | 0,37 |
| KAB HALMAHERA TENGAH | 0,27 | 0,52 | 0,75 |
| KOTA TERNATE | 1,74 | 0,90 | -0,82 |
| MANOKWARI | 0,02 | -0,65 | 0,05 |
| KAB SORONG | -0,12 | 0,05 | 0,38 |
| KAB SORONG SELATAN | 0,20 | -0,11 | 0,20 |
| KOTA SORONG | 0,29 | -0,81 | 1,35 |
| KOTA JAYAPURA | -0,36 | 0,06 | 0,70 |
| MERAUKE | 1,06 | 0,59 | 0,35 |
| TIMIKA | 0,28 | 0,32 | 0,26 |
| KAB NABIRE | -1,40 | -0,71 | 0,27 |
| KAB JAYAWIJAYA | -0,05 | 0,49 | 2,57 |
| INDONESIA | -0,15 | 0,68 | 0,41 |

## Generated Pydantic model

```python
from pydantic import BaseModel, Field


class BpsInflasiMomRecord(BaseModel):
    kota_inflasi: str | None = Field(default=None, alias="Kota_Inflasi")
    januari_s_d_desember: float | None = Field(default=None, alias="Januari s.d. Desember (12 kolom terpisah per bulan)")
    tahunan: float | None = Field(default=None, alias="Tahunan")
    sample_data: str | None = Field(default=None, alias="Sample Data:")
    kota_inflasi: str | None = Field(default=None, alias="Kota Inflasi")
    kab_aceh_tengah: str | None = Field(default=None, alias="KAB ACEH TENGAH")
    kota_meulaboh: str | None = Field(default=None, alias="KOTA MEULABOH")
    kab_aceh_tamiang: str | None = Field(default=None, alias="KAB ACEH TAMIANG")
    kota_banda_aceh: str | None = Field(default=None, alias="KOTA BANDA ACEH")
    kota_lhokseumawe: str | None = Field(default=None, alias="KOTA LHOKSEUMAWE")
    kab_labuhanbatu: str | None = Field(default=None, alias="KAB LABUHANBATU")
    kab_karo: str | None = Field(default=None, alias="KAB KARO")
    kab_deli_serdang: str | None = Field(default=None, alias="KAB DELI SERDANG")
    kota_sibolga: str | None = Field(default=None, alias="KOTA SIBOLGA")
    kota_pematang_siantar: str | None = Field(default=None, alias="KOTA PEMATANG SIANTAR")
    kota_medan: str | None = Field(default=None, alias="KOTA MEDAN")
    kota_padangsidimpuan: str | None = Field(default=None, alias="KOTA PADANGSIDIMPUAN")
    kota_gunungsitoli: str | None = Field(default=None, alias="KOTA GUNUNGSITOLI")
    kab_dharmasraya: str | None = Field(default=None, alias="KAB DHARMASRAYA")
    kab_pasaman_barat: str | None = Field(default=None, alias="KAB PASAMAN BARAT")
    kota_padang: str | None = Field(default=None, alias="KOTA PADANG")
    kota_bukittinggi: str | None = Field(default=None, alias="KOTA BUKITTINGGI")
    tembilahan: str | None = Field(default=None, alias="TEMBILAHAN")
    kab_kampar: str | None = Field(default=None, alias="KAB KAMPAR")
    kota_pekanbaru: str | None = Field(default=None, alias="KOTA PEKANBARU")
    kota_dumai: str | None = Field(default=None, alias="KOTA DUMAI")
    kab_kerinci: str | None = Field(default=None, alias="KAB KERINCI")
    bungo: str | None = Field(default=None, alias="BUNGO")
    kota_jambi: str | None = Field(default=None, alias="KOTA JAMBI")
    kab_ogan_komering_ilir: str | None = Field(default=None, alias="KAB OGAN KOMERING ILIR")
    kab_muara_enim: str | None = Field(default=None, alias="KAB MUARA ENIM")
    kota_palembang: str | None = Field(default=None, alias="KOTA PALEMBANG")
    kota_lubuklinggau: str | None = Field(default=None, alias="KOTA LUBUKLINGGAU")
    kab_muko_muko: str | None = Field(default=None, alias="KAB MUKO MUKO")
    kota_bengkulu: str | None = Field(default=None, alias="KOTA BENGKULU")
    kab_lampung_timur: str | None = Field(default=None, alias="KAB LAMPUNG TIMUR")
    kab_mesuji: str | None = Field(default=None, alias="KAB MESUJI")
    kota_bandar_lampung: str | None = Field(default=None, alias="KOTA BANDAR LAMPUNG")
    kota_metro: str | None = Field(default=None, alias="KOTA METRO")
    tanjung_pandan: str | None = Field(default=None, alias="TANJUNG PANDAN")
    kab_bangka_barat: str | None = Field(default=None, alias="KAB BANGKA BARAT")
    kab_belitung_timur: str | None = Field(default=None, alias="KAB BELITUNG TIMUR")
    kota_pangkal_pinang: str | None = Field(default=None, alias="KOTA PANGKAL PINANG")
    kab_karimun: str | None = Field(default=None, alias="KAB KARIMUN")
    kota_batam: str | None = Field(default=None, alias="KOTA BATAM")
    kota_tanjung_pinang: str | None = Field(default=None, alias="KOTA TANJUNG PINANG")
    dki_jakarta: str | None = Field(default=None, alias="DKI JAKARTA")
    kab_bandung: str | None = Field(default=None, alias="KAB BANDUNG")
    kab_majalengka: str | None = Field(default=None, alias="KAB MAJALENGKA")
    kab_subang: str | None = Field(default=None, alias="KAB SUBANG")
    kota_bogor: str | None = Field(default=None, alias="KOTA BOGOR")
    kota_sukabumi: str | None = Field(default=None, alias="KOTA SUKABUMI")
    kota_bandung: str | None = Field(default=None, alias="KOTA BANDUNG")
    kota_cirebon: str | None = Field(default=None, alias="KOTA CIREBON")
    kota_bekasi: str | None = Field(default=None, alias="KOTA BEKASI")
    kota_depok: str | None = Field(default=None, alias="KOTA DEPOK")
    kota_tasikmalaya: str | None = Field(default=None, alias="KOTA TASIKMALAYA")
    cilacap: str | None = Field(default=None, alias="CILACAP")
    purwokerto: str | None = Field(default=None, alias="PURWOKERTO")
    kab_wonosobo: str | None = Field(default=None, alias="KAB WONOSOBO")
    kab_wonogiri: str | None = Field(default=None, alias="KAB WONOGIRI")
    kab_rembang: str | None = Field(default=None, alias="KAB REMBANG")
    kudus: str | None = Field(default=None, alias="KUDUS")
    kota_surakarta: str | None = Field(default=None, alias="KOTA SURAKARTA")
    kota_semarang: str | None = Field(default=None, alias="KOTA SEMARANG")
    kota_tegal: str | None = Field(default=None, alias="KOTA TEGAL")
    kab_gunungkidul: str | None = Field(default=None, alias="KAB GUNUNGKIDUL")
    kota_yogyakarta: str | None = Field(default=None, alias="KOTA YOGYAKARTA")
    kab_tulungagung: str | None = Field(default=None, alias="KAB TULUNGAGUNG")
    jember: str | None = Field(default=None, alias="JEMBER")
    banyuwangi: str | None = Field(default=None, alias="BANYUWANGI")
    kab_bojonegoro: str | None = Field(default=None, alias="KAB BOJONEGORO")
    kab_gresik: str | None = Field(default=None, alias="KAB GRESIK")
    sumenep: str | None = Field(default=None, alias="SUMENEP")
    kota_kediri: str | None = Field(default=None, alias="KOTA KEDIRI")
    kota_malang: str | None = Field(default=None, alias="KOTA MALANG")
    kota_probolinggo: str | None = Field(default=None, alias="KOTA PROBOLINGGO")
    kota_madiun: str | None = Field(default=None, alias="KOTA MADIUN")
    kota_surabaya: str | None = Field(default=None, alias="KOTA SURABAYA")
    kab_pandeglang: str | None = Field(default=None, alias="KAB PANDEGLANG")
    kab_lebak: str | None = Field(default=None, alias="KAB LEBAK")
    kota_tangerang: str | None = Field(default=None, alias="KOTA TANGERANG")
    kota_cilegon: str | None = Field(default=None, alias="KOTA CILEGON")
    kota_serang: str | None = Field(default=None, alias="KOTA SERANG")
    kab_tabanan: str | None = Field(default=None, alias="KAB TABANAN")
    kab_badung: str | None = Field(default=None, alias="KAB BADUNG")
    singaraja: str | None = Field(default=None, alias="SINGARAJA")
    kota_denpasar: str | None = Field(default=None, alias="KOTA DENPASAR")
    kab_sumbawa: str | None = Field(default=None, alias="KAB SUMBAWA")
    kota_mataram: str | None = Field(default=None, alias="KOTA MATARAM")
    kota_bima: str | None = Field(default=None, alias="KOTA BIMA")
    waingapu: str | None = Field(default=None, alias="WAINGAPU")
    kab_timor_tengah_selatan: str | None = Field(default=None, alias="KAB TIMOR TENGAH SELATAN")
    maumere: str | None = Field(default=None, alias="MAUMERE")
    kab_ngada: str | None = Field(default=None, alias="KAB NGADA")
    kota_kupang: str | None = Field(default=None, alias="KOTA KUPANG")
    dili: str | None = Field(default=None, alias="DILI")
    kab_ketapang: str | None = Field(default=None, alias="KAB KETAPANG")
    sintang: str | None = Field(default=None, alias="SINTANG")
    kab_kayong_utara: str | None = Field(default=None, alias="KAB KAYONG UTARA")
    kota_pontianak: str | None = Field(default=None, alias="KOTA PONTIANAK")
    kota_singkawang: str | None = Field(default=None, alias="KOTA SINGKAWANG")
    sampit: str | None = Field(default=None, alias="SAMPIT")
    kab_kapuas: str | None = Field(default=None, alias="KAB KAPUAS")
    kab_sukamara: str | None = Field(default=None, alias="KAB SUKAMARA")
    kota_palangka_raya: str | None = Field(default=None, alias="KOTA PALANGKA RAYA")
    kab_tanah_laut: str | None = Field(default=None, alias="KAB TANAH LAUT")
    kotabaru: str | None = Field(default=None, alias="KOTABARU")
    kab_hulu_sungai_tengah: str | None = Field(default=None, alias="KAB HULU SUNGAI TENGAH")
    tanjung: str | None = Field(default=None, alias="TANJUNG")
    kota_banjarmasin: str | None = Field(default=None, alias="KOTA BANJARMASIN")
    kab_berau: str | None = Field(default=None, alias="KAB BERAU")
    kab_penajam_paser_utara: str | None = Field(default=None, alias="KAB PENAJAM PASER UTARA")
    kota_balikpapan: str | None = Field(default=None, alias="KOTA BALIKPAPAN")
    kota_samarinda: str | None = Field(default=None, alias="KOTA SAMARINDA")
    tanjung_selor: str | None = Field(default=None, alias="TANJUNG SELOR")
    kab_nunukan: str | None = Field(default=None, alias="KAB NUNUKAN")
    kota_tarakan: str | None = Field(default=None, alias="KOTA TARAKAN")
    kab_minahasa_selatan: str | None = Field(default=None, alias="KAB MINAHASA SELATAN")
    kab_minahasa_utara: str | None = Field(default=None, alias="KAB MINAHASA UTARA")
    kota_manado: str | None = Field(default=None, alias="KOTA MANADO")
    kota_kotamobagu: str | None = Field(default=None, alias="KOTA KOTAMOBAGU")
    luwuk: str | None = Field(default=None, alias="LUWUK")
    kab_morowali: str | None = Field(default=None, alias="KAB MOROWALI")
    kab_toli_toli: str | None = Field(default=None, alias="KAB TOLI TOLI")
    kota_palu: str | None = Field(default=None, alias="KOTA PALU")
    bulukumba: str | None = Field(default=None, alias="BULUKUMBA")
    watampone: str | None = Field(default=None, alias="WATAMPONE")
    kab_wajo: str | None = Field(default=None, alias="KAB WAJO")
    kab_sidenreng_rappang: str | None = Field(default=None, alias="KAB SIDENRENG RAPPANG")
    kab_luwu_timur: str | None = Field(default=None, alias="KAB LUWU TIMUR")
    kota_makassar: str | None = Field(default=None, alias="KOTA MAKASSAR")
    kota_pare_pare: str | None = Field(default=None, alias="KOTA PARE-PARE")
    kota_palopo: str | None = Field(default=None, alias="KOTA PALOPO")
    kab_konawe: str | None = Field(default=None, alias="KAB KONAWE")
    kab_kolaka: str | None = Field(default=None, alias="KAB KOLAKA")
    kota_kendari: str | None = Field(default=None, alias="KOTA KENDARI")
    kota_bau_bau: str | None = Field(default=None, alias="KOTA BAU-BAU")
    kab_gorontalo: str | None = Field(default=None, alias="KAB GORONTALO")
    kota_gorontalo: str | None = Field(default=None, alias="KOTA GORONTALO")
    kab_majene: str | None = Field(default=None, alias="KAB MAJENE")
    mamuju: str | None = Field(default=None, alias="MAMUJU")
    kab_maluku_tengah: str | None = Field(default=None, alias="KAB MALUKU TENGAH")
    kota_ambon: str | None = Field(default=None, alias="KOTA AMBON")
    kota_tual: str | None = Field(default=None, alias="KOTA TUAL")
    kab_halmahera_tengah: str | None = Field(default=None, alias="KAB HALMAHERA TENGAH")
    kota_ternate: str | None = Field(default=None, alias="KOTA TERNATE")
    manokwari: str | None = Field(default=None, alias="MANOKWARI")
    kab_sorong: str | None = Field(default=None, alias="KAB SORONG")
    kab_sorong_selatan: str | None = Field(default=None, alias="KAB SORONG SELATAN")
    kota_sorong: str | None = Field(default=None, alias="KOTA SORONG")
    kota_jayapura: str | None = Field(default=None, alias="KOTA JAYAPURA")
    merauke: str | None = Field(default=None, alias="MERAUKE")
    timika: str | None = Field(default=None, alias="TIMIKA")
    kab_nabire: str | None = Field(default=None, alias="KAB NABIRE")
    kab_jayawijaya: str | None = Field(default=None, alias="KAB JAYAWIJAYA")
    indonesia: str | None = Field(default=None, alias="INDONESIA")

    model_config = {"populate_by_name": True, "extra": "ignore"}
```

> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. Keep `extra="ignore"` so new source columns do not break validation.
