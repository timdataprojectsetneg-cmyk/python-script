# Use Case: geopolitik

Data catalog and environment specifications for Use Case Geopolitik.

Source count: **58** · Active / Implemented: **55** · Takeout: **3**

## Sources

| # | Source Name | Publisher | Module / Source | Data Access | Primary Target Table | Status |
|---|---|---|---|---|---|---|
| 1 | NOTAM Ruang Udara | AirNav | `notam` | Web Scraping / FAA API | `raw_airnav_notam` | DONE |
| 2 | Klarifikasi Hoaks Geopolitik | CekFakta | `klarifikasi_hoaks` | Web Scraping CekFakta.com | `raw_cekfakta_klarifikasi_hoaks` | TAKEOUT |
| 3 | AMTI Insiden Maritim LCS | CSIS | `amti_insiden_maritim` | Web Scraping AMTI Tracker | `raw_csis_amti_insiden_maritim` | DONE |
| 4 | Harga Minyak Mentah ICP | ESDM | `harga_minyak_mentah_icp` | Web Scraping Ditjen Migas | `raw_esdm_harga_minyak_mentah_icp` | DONE |
| 5 | Kedaruratan Bencana Global | GDACS | `kedaruratan_bencana` | RSS / XML Feed | `raw_gdacs_kedaruratan_bencana` | DONE |
| 6 | Berita Media Asing Global | GDELT | `media_asing` | REST API (GDELT DOC 2.0) | `raw_gdelt_media_asing` | TAKEOUT |
| 7 | Chokepoints Maritim Global | IMF | `chokepoints_maritim` | ArcGIS FeatureServer PortWatch | `raw_imf_chokepoints` | DONE |
| 8 | Iuran Organisasi Internasional | Kemlu | `iuran_organisasi_internasional` | Satu Data Kemlu API | `raw_kemlu_iuran_organisasi_internasional` | DONE |
| 9 | Penanganan Kasus WNI Luar Negeri | Kemlu | `kasus_wni` | Portal Peduli WNI | `raw_kemlu_kasus_wni` | DONE |
| 10 | Safe Travel Himbauan Keamanan | Kemlu | `safe_travel` | Safe Travel REST API | `raw_kemlu_safe_travel` | DONE |
| 11 | Sebaran WNI & PMI di Dunia | Kemlu | `sebaran_wni_pmi` | Satu Data Kemlu API | `raw_kemlu_sebaran_wni_pmi` | DONE |
| 12 | Treaty Room Traktat Internasional | Kemlu | `treaty_room` | Treaty Room Kemlu API | `raw_kemlu_treaty_room` | DONE |
| 13 | OFAC Sanksi Perdagangan & SDN | OFAC | `sanksi_perdagangan` | Specially Designated Nationals CSV | `raw_ofac_sanksi_perdagangan` | DONE |
| 14 | Pertemuan Bilateral RI | Setpres | `pertemuan_bilateral` | Web Scraping Siaran Pers | `raw_setpres_pertemuan_bilateral` | DONE |
| 15 | Belanja Militer Global | SIPRI | `belanja_militer` | Download Excel Database | `raw_sipri_belanja_militer` | DONE |
| 16 | Data Konflik Global (UCDP GED) | UCDP | `konflik_global` | Direct Download CSV Candidate GED | `raw_ucdp_konflik_global` | DONE |
| 17 | UN Comtrade Plus Trade Flow | UN | `comtrade` | REST API / Portal BPS Exim | `raw_un_comtrade` | DONE |
| 18 | Status Traktat Multilateral PBB | UN | `status_traktat_multilateral` | UN Treaties Search HTML | `raw_un_status_traktat_multilateral` | DONE |
| 19 | Rekam Voting Sidang Majelis PBB | UN | `voting_sidang_pbb` | UN Digital Library Voting Data | `raw_un_voting_sidang_pbb` | DONE |
| 20 | Human Development Index (HDI) | UNDP | `hdi` | Composite Indices CSV | `raw_undp_hdi` | DONE |
| 21 | Global Innovation Index (GII) | WIPO | `global_innovation_index` | WIPO Global Innovation Data | `raw_wipo_global_innovation_index` | DONE |
| 22 | Indikator Makroekonomi Dunia | World Bank | `indikator_makro` | World Bank Indicators V2 API | `raw_world_bank_indikator_makro` | DONE |
| 23 | BPS Ekspor Impor Bulanan | BPS | `ekspor_impor_bulanan` | Web Scraping BPS Exim (Next.js server action) | `raw_bps_ekspor_impor_bulanan` | DONE |
| 24 | Ekspor Sektor Kemendag | Kemendag | `ekspor_sektor` | Web Scraping Satu Data Kemendag | `raw_kemendag_ekspor_sektor` | DONE |
| 25 | Impor Golongan Kemendag | Kemendag | `impor_golongan` | Web Scraping Satu Data Kemendag | `raw_kemendag_impor_golongan` | DONE |
| 26 | Perjanjian Perdagangan (FTA) | Kemendag | `perjanjian_perdagangan` | Web Scraping FTA Support Center | `raw_kemendag_perjanjian_perdagangan` | DONE |
| 27 | Ekspor Impor Mitra (Comtrade preview) | UN | `ekspor_impor_mitra` | REST API UN Comtrade public preview | `raw_un_ekspor_impor_mitra` | DONE |
| 28 | Impor Komoditas Strategis | UN | `impor_komoditas_strategis` | REST API UN Comtrade public preview | `raw_un_impor_komoditas_strategis` | DONE |
| 29 | Lead Time Logistik Indonesia | World Bank | `lead_time_logistik` | World Bank Indicators V2 API | `raw_world_bank_lead_time_logistik` | DONE |
| 30 | Harga Komoditas Dunia (Pink Sheet) | World Bank | `harga_komoditas_dunia` | Download Excel CMO Monthly | `raw_world_bank_harga_komoditas_dunia` | DONE |
| 31 | Profil Negara Mitra | World Bank | `profil_negara_mitra` | World Bank Country API | `raw_world_bank_profil_negara_mitra` | DONE |
| 32 | Stabilitas Politik WGI | World Bank | `stabilitas_politik_wgi` | Download CSV zip WGI | `raw_world_bank_stabilitas_politik_wgi` | DONE |
| 33 | Harga Brent Harian | EIA | `harga_brent_harian` | EIA API v2 | `raw_eia_harga_brent_harian` | DONE |
| 34 | Indeks Harga Pangan FAO | FAO | `indeks_harga_pangan` | Download CSV FAO | `raw_fao_indeks_harga_pangan` | DONE |
| 35 | Indeks Risiko Geopolitik (GPR) | Caldara & Iacoviello | `indeks_risiko_geopolitik` | Download Stata .dta | `raw_caldara_iacoviello_indeks_risiko_geopolitik` | DONE |
| 36 | Insiden Pelayaran UKMTO | UKMTO | `insiden_pelayaran` | REST API (impersonate chrome) | `raw_ukmto_insiden_pelayaran` | DONE |
| 37 | Gempa Dirasakan BMKG | BMKG | `gempa_dirasakan` | XML data.bmkg.go.id | `raw_bmkg_gempa_dirasakan` | DONE |
| 38 | Kejadian Bencana BNPB | BNPB | `kejadian_bencana` | ArcGIS FeatureServer / Excel manual | `raw_bnpb_kejadian_bencana` | PARTIAL |
| 39 | Ekspor HS Pertanian | Kementan | `ekspor_hs_pertanian` | Web Scraping Eksim Pertanian | `raw_pertanian_ekspor_hs_pertanian` | DONE |
| 40 | Impor HS Pertanian | Kementan | `impor_hs_pertanian` | Web Scraping Eksim Pertanian | `raw_pertanian_impor_hs_pertanian` | DONE |
| 41 | Ekspor Perikanan | KKP | `ekspor_perikanan` | JSON API Portal Data KKP | `raw_kkp_ekspor_perikanan` | DONE |
| 42 | Perubahan Tarif PMK 50/2026 | Bea Cukai | `perubahan_tarif_pmk` | PDF Peraturan (pypdf) | `raw_beacukai_perubahan_tarif_pmk` | DONE |
| 43 | PMA Negara Asal | BKPM | `pma_negara_asal` | PDF Rilis Realisasi Investasi (pypdf) | `raw_bkpm_pma_negara_asal` | DONE |
| 44 | Daftar Keanggotaan OI | Kemlu | `daftar_keanggotaan_oi` | PDF Kemlu (pypdf) | `raw_kemlu_daftar_keanggotaan_oi` | DONE |
| 45 | Keanggotaan Forum Bank Dunia | World Bank | `keanggotaan_forum` | Web Scraping worldbank.org | `raw_world_bank_keanggotaan_forum` | DONE |
| 46 | Agenda Forum ASEAN | ASEAN | `agenda_forum` | PDF Notional Calendar (pypdf) | `raw_asean_agenda_forum` | DONE |
| 47 | Hasil Forum ASEAN | ASEAN | `hasil_forum` | PDF Chairman's Statement (pypdf) | `raw_asean_hasil_forum` | DONE |
| 48 | Target Komitmen Iklim (NDC) | UNFCCC | `target_komitmen_iklim` | PDF NDC (pypdf, rule-based) | `raw_unfccc_target_komitmen_iklim` | PARTIAL |
| 49 | Penempatan PMI | BP2MI | `penempatan_pmi` | PDF Statistik BP2MI (pypdf) | `raw_bp2mi_penempatan_pmi` | DONE |
| 50 | Pengaduan PMI | BP2MI | `pengaduan_pmi` | PDF Statistik BP2MI (pypdf) | `raw_bp2mi_pengaduan_pmi` | DONE |
| 51 | Kasus Pelindungan WNI (LKJ PWNI) | Kemlu | `kasus_pelindungan_wni` | PDF LKJ Dit. PWNI (pypdf) | `raw_kemlu_kasus_pelindungan_wni` | DONE |
| 52 | Riwayat Evakuasi WNI | Kemlu | `riwayat_evakuasi_wni` | PDF Renstra Dit. PWNI (pypdf) | `raw_kemlu_riwayat_evakuasi_wni` | DONE |
| 53 | Imbauan dan Status Siaga | Kemlu | `imbauan_status_siaga` | Scraping artikel kemlu.go.id (URL/file manual) | `raw_kemlu_imbauan_status_siaga` | TAKEOUT |
| 54 | Notifikasi ePing (SPS/TBT) | WTO | `eping_notifikasi` | REST API epingalert.org | `raw_wto_eping_notifikasi` | DONE |
| 55 | Sengketa Dagang Indonesia | WTO | `sengketa_dagang` | Web Scraping wto.org dispute pages | `raw_wto_sengketa_dagang` | DONE |
| 56 | Kontrol Ekspor AS (BIS) | Federal Register | `kontrol_ekspor_as` | REST API federalregister.gov | `raw_federal_register_kontrol_ekspor_as` | DONE |
| 57 | Posisi Resmi Indonesia | Setpres | `posisi_resmi_indonesia` | Web Scraping Pernyataan Pers Bersama | `raw_setpres_posisi_resmi_indonesia` | DONE |
| 58 | Kesepakatan RI-Tiongkok | Setpres | `kesepakatan_ri_tiongkok` | Web Scraping Siaran Pers Setneg | `raw_setpres_kesepakatan_ri_tiongkok` | DONE |
