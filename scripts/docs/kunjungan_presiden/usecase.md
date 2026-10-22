# Use Case: kunjungan_presiden

Data catalog and environment specifications for Use Case Kunjungan Presiden.

Source count: **16** · Active / Implemented: **15** · Takeout: **1**

## Sources

| # | Source Name | Publisher | Module / Source | Data Access | Primary Target Table | Status |
|---|---|---|---|---|---|---|
| 1 | SPPG Dapur MBG | BGN | `sppg_mbg` | REST API (GIS GINA BGN) | `raw_bgn_sppg_mbg` | DONE |
| 2 | Prakiraan Cuaca Wilayah | BMKG | `prakiraan_cuaca` | REST API (BMKG Publik) | `raw_bmkg_prakiraan_cuaca` | DONE |
| 3 | Profil Sosioekonomi Daerah | BPS | `profil_sosioekonomi` | Web API BPS (App ID Key) | `raw_bps_profil_sosioekonomi` | DONE |
| 4 | Sentimen Wilayah MBG & Koperasi | GDELT | `sentimen_wilayah` | REST API (GDELT DOC 2.0) | `raw_gdelt_sentimen_wilayah` | TAKEOUT |
| 5 | Susunan Pemerintahan Daerah | Kemendagri | `susunan_pemerintahan_daerah` | Web Scraping / PELITA | `raw_kemendagri_susunan_pemerintahan_daerah` | DONE |
| 6 | Indeks Desa Membangun (IDM) | Kemendesa | `idm` | Open REST API | `raw_kemendesa_idm` | DONE |
| 7 | Fasilitas & Sarpras Bandara | Kemenhub | `hubud_bandara` | ArcGIS REST FeatureServer | `raw_kemenhub_hubud_bandara` | DONE |
| 8 | Pemeriksaan CKG Fasyankes | Kemenkes | `satusehat_ckg` | FHIR-ID Observation REST API | `raw_kemenkes_satusehat_ckg` | DONE |
| 9 | Ketersediaan Tempat Tidur RS | Kemenkes | `siranap_rs_rujukan` | Web Scraping SIRANAP | `raw_kemenkes_siranap_rs_rujukan` | DONE |
| 10 | Potensi Koperasi Desa KDMP | Kemenkop | `simkopdes_kdmp` | REST API SIMKOPDES | `raw_kemenkop_simkopdes_kdmp` | DONE |
| 11 | Kampung Nelayan Merah Putih | KKP | `kampung_nelayan_merah_putih` | Web Scraping PIPP KKP | `raw_kkp_kampung_nelayan_merah_putih` | DONE |
| 12 | Rekap Aduan Publik SP4N-LAPOR! | LAPOR! | `rekap_aduan_wilayah` | DWH Maps REST API | `raw_lapor_aduan` | DONE |
| 13 | Matriks Janji & Komitmen Presiden | Setkab | `matriks_janji_presiden` | Web Scraping Setkab.go.id | `raw_setkab_matriks_janji_presiden` | DONE |
| 14 | Tracking Arahan Lapangan Presiden | Setkab | `tracking_arahan_lapangan` | Web Scraping Setkab.go.id | `raw_setkab_tracking_arahan_lapangan` | DONE |
| 15 | Matriks Risiko Kunjungan Kerja | Setpres | `matriks_risiko_kunjungan` | Web Scraping Setneg.go.id | `raw_setpres_matriks_risiko_kunjungan` | DONE |
| 16 | Statistik Kunjungan Kerja Presiden | Setpres | `statistik_kunjungan_presiden` | Web Scraping Tabular | `raw_setpres_statistik_kunjungan_presiden` | DONE |
