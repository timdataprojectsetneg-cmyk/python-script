# Use Case: geopolitik

Data catalog and environment specifications for Use Case Geopolitik.

Source count: **22** · Active / Implemented: **19** · Takeout: **3**

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
