-- DDL Initialization with Column Comments/Descriptions for Kunjungan Presiden & Geopolitik
-- Deskripsi kolom diambil langsung dari Data Dictionary Excel / KAK
-- Kompatibel dengan DBeaver, pgAdmin, dan PostgreSQL 14+

-- ========================================================
-- USECASE: KUNJUNGAN_PRESIDEN (Schema: raw_kunker)
-- ========================================================
CREATE SCHEMA IF NOT EXISTS raw_kunker;

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_bgn_sppg_mbg (Sumber: bgn/sppg_mbg)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_bgn_sppg_mbg (
    id_sppg TEXT,
    nama_sppg TEXT,
    provinsi TEXT,
    kabupaten_kota TEXT,
    kecamatan TEXT,
    kapasitas_porsi_harian BIGINT,
    jumlah_penerima_manfaat BIGINT,
    status_operasional TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    data_source TEXT,
    PRIMARY KEY (id_sppg)
);

COMMENT ON TABLE raw_kunker.raw_bgn_sppg_mbg IS 'bgn sppg_mbg';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.id_sppg IS 'Identifier unik Satuan Pelayanan Pemenuhan Gizi (contoh: SPPG-3302-001).';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.nama_sppg IS 'Nama unit dapur pelayanan gizi Makan Bergizi Gratis.';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.provinsi IS 'Provinsi wilayah operasional dapur.';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.kabupaten_kota IS 'Kabupaten atau kota lokasi dapur.';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.kecamatan IS 'Kecamatan lokasi dapur.';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.kapasitas_porsi_harian IS 'Kapasitas produksi makanan bergizi per hari (porsi/hari).';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.jumlah_penerima_manfaat IS 'Jumlah sasaran siswa dan balita penerima manfaat terlayani (jiwa).';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.status_operasional IS 'Status operasional unit dapur (Aktif, Persiapan, Uji Coba).';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.latitude IS 'Koordinat lintang lokasi dapur.';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.longitude IS 'Koordinat bujur lokasi dapur.';
COMMENT ON COLUMN raw_kunker.raw_bgn_sppg_mbg.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_bmkg_prakiraan_cuaca (Sumber: bmkg/prakiraan_cuaca)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_bmkg_prakiraan_cuaca (
    adm4 TEXT,
    provinsi TEXT,
    kotkab TEXT,
    kecamatan TEXT,
    desa TEXT,
    lon DOUBLE PRECISION,
    lat DOUBLE PRECISION,
    timezone TEXT,
    local_datetime TEXT,
    utc_datetime TEXT,
    t DOUBLE PRECISION,
    hu DOUBLE PRECISION,
    weather_desc TEXT,
    weather_desc_en TEXT,
    ws DOUBLE PRECISION,
    wd TEXT,
    tcc DOUBLE PRECISION,
    vs_text TEXT,
    analysis_date TEXT
);

COMMENT ON TABLE raw_kunker.raw_bmkg_prakiraan_cuaca IS 'bmkg prakiraan_cuaca';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.adm4 IS 'Kode wilayah administrasi tingkat IV (kelurahan/desa).';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.provinsi IS 'Nama provinsi.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.kotkab IS 'Nama kabupaten/kota.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.kecamatan IS 'Nama kecamatan.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.desa IS 'Nama desa/kelurahan.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.lon IS 'Longitude lokasi administrasi.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.lat IS 'Latitude lokasi administrasi.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.timezone IS 'Zona waktu lokasi.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.local_datetime IS 'Waktu prakiraan lokal (WIB/WITA/WIT).';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.utc_datetime IS 'Waktu prakiraan UTC.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.t IS 'Suhu udara (derajat Celsius).';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.hu IS 'Kelembapan udara (%).';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.weather_desc IS 'Kondisi cuaca dalam Bahasa Indonesia.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.weather_desc_en IS 'Kondisi cuaca dalam Bahasa Inggris.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.ws IS 'Kecepatan angin (km/jam).';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.wd IS 'Arah angin.';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.tcc IS 'Tutupan awan (%).';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.vs_text IS 'Jarak pandang (km).';
COMMENT ON COLUMN raw_kunker.raw_bmkg_prakiraan_cuaca.analysis_date IS 'Waktu analisis produksi data prakiraan.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_bps_profil_sosioekonomi (Sumber: bps/profil_sosioekonomi)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_bps_profil_sosioekonomi (
    kode_wilayah_kemendagri TEXT,
    provinsi TEXT,
    kabupaten_kota TEXT,
    jumlah_penduduk_jiwa BIGINT,
    kepadatan_penduduk_km2 DOUBLE PRECISION,
    persentase_penduduk_miskin DOUBLE PRECISION,
    tingkat_pengangguran_terbuka_tpt DOUBLE PRECISION,
    indeks_pembangunan_manusia_ipm DOUBLE PRECISION,
    pertumbuhan_ekonomi_pdrb_pct DOUBLE PRECISION,
    pdrb_harga_berlaku_juta_rp DOUBLE PRECISION,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_bps_profil_sosioekonomi IS 'bps profil_sosioekonomi';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.kode_wilayah_kemendagri IS 'Kode wilayah administrasi Kemendagri (contoh: 33.02, 32.04).';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.provinsi IS 'Nama provinsi (contoh: Jawa Tengah, Jawa Barat, Jawa Timur).';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.kabupaten_kota IS 'Nama kabupaten/kota sasaran (contoh: Kabupaten Banyumas, Kabupaten Bandung).';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.jumlah_penduduk_jiwa IS 'Jumlah penduduk total semesteran (jiwa).';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.kepadatan_penduduk_km2 IS 'Kepadatan penduduk per km persegi (jiwa/km2).';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.persentase_penduduk_miskin IS 'Persentase penduduk miskin daerah (%).';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.tingkat_pengangguran_terbuka_tpt IS 'Tingkat Pengangguran Terbuka daerah / TPT (%).';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.indeks_pembangunan_manusia_ipm IS 'Indeks Pembangunan Manusia / IPM daerah (skor 0-100).';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.pertumbuhan_ekonomi_pdrb_pct IS 'Laju pertumbuhan PDRB riil tahunan (%).';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.pdrb_harga_berlaku_juta_rp IS 'Nominal PDRB Atas Dasar Harga Berlaku (Juta Rupiah).';
COMMENT ON COLUMN raw_kunker.raw_bps_profil_sosioekonomi.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_gdelt_sentimen_wilayah (Sumber: gdelt/sentimen_wilayah)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_gdelt_sentimen_wilayah (
    tanggal_pemantauan TEXT,
    nama_program_prioritas TEXT,
    provinsi_wilayah TEXT,
    volume_percakapan_media BIGINT,
    sentimen_positif_pct DOUBLE PRECISION,
    sentimen_netral_pct DOUBLE PRECISION,
    sentimen_negatif_pct DOUBLE PRECISION,
    isu_dominan_diperbincangkan TEXT,
    kanal_utama_sumber TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_gdelt_sentimen_wilayah IS 'gdelt sentimen_wilayah';
COMMENT ON COLUMN raw_kunker.raw_gdelt_sentimen_wilayah.tanggal_pemantauan IS 'Waktu monitoring percakapan publik (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_kunker.raw_gdelt_sentimen_wilayah.nama_program_prioritas IS 'Nama program prioritas (Makan Bergizi Gratis (MBG), Koperasi Desa Merah Putih, Penurunan Stunting, Cek Kesehatan Gratis (CKG), PSN).';
COMMENT ON COLUMN raw_kunker.raw_gdelt_sentimen_wilayah.provinsi_wilayah IS 'Provinsi sasaran pemantauan isu (Jawa Tengah, Jawa Barat, Jawa Timur, dll.).';
COMMENT ON COLUMN raw_kunker.raw_gdelt_sentimen_wilayah.volume_percakapan_media IS 'Jumlah mention dan artikel yang beredar di ruang publik.';
COMMENT ON COLUMN raw_kunker.raw_gdelt_sentimen_wilayah.sentimen_positif_pct IS 'Proporsi sentimen positif publik (%)';
COMMENT ON COLUMN raw_kunker.raw_gdelt_sentimen_wilayah.sentimen_netral_pct IS 'Proporsi sentimen netral publik (%)';
COMMENT ON COLUMN raw_kunker.raw_gdelt_sentimen_wilayah.sentimen_negatif_pct IS 'Proporsi sentimen kritis / negatif publik (%)';
COMMENT ON COLUMN raw_kunker.raw_gdelt_sentimen_wilayah.isu_dominan_diperbincangkan IS 'Substansi narasi utama di ruang publik lokal.';
COMMENT ON COLUMN raw_kunker.raw_gdelt_sentimen_wilayah.kanal_utama_sumber IS 'Kanal percakapan terbanyak (Media Daring, X/Twitter, Instagram, Portal Berita).';
COMMENT ON COLUMN raw_kunker.raw_gdelt_sentimen_wilayah.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah (Sumber: kemendagri/susunan_pemerintahan_daerah)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah (
    kode_daerah TEXT,
    provinsi TEXT,
    kabupaten_kota TEXT,
    nama_kepala_daerah TEXT,
    status_jabatan TEXT,
    partai_pengusung_koalisi TEXT,
    nama_ketua_dprd TEXT,
    partai_ketua_dprd TEXT,
    komposisi_kursi_dprd TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah IS 'kemendagri susunan_pemerintahan_daerah';
COMMENT ON COLUMN raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah.kode_daerah IS 'Kode wilayah administrasi Kemendagri (misal: ''33.02'').';
COMMENT ON COLUMN raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah.provinsi IS 'Nama provinsi tempat kabupaten/kota berada.';
COMMENT ON COLUMN raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah.kabupaten_kota IS 'Nama kabupaten atau kota administrasi.';
COMMENT ON COLUMN raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah.nama_kepala_daerah IS 'Nama lengkap Bupati / Walikota / Gubernur / Penjabat Kepala Daerah.';
COMMENT ON COLUMN raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah.status_jabatan IS 'Status jabatan kepala daerah (Definitif, Penjabat / Pj, Pelaksana Tugas / Plt).';
COMMENT ON COLUMN raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah.partai_pengusung_koalisi IS 'Partai politik atau koalisi pengusung kepala daerah terpilih.';
COMMENT ON COLUMN raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah.nama_ketua_dprd IS 'Nama Ketua DPRD Kabupaten/Kota.';
COMMENT ON COLUMN raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah.partai_ketua_dprd IS 'Partai politik asal Ketua DPRD.';
COMMENT ON COLUMN raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah.komposisi_kursi_dprd IS 'Distribusi perolehan kursi partai di DPRD (ringkasan tekstual).';
COMMENT ON COLUMN raw_kunker.raw_kemendagri_susunan_pemerintahan_daerah.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_kemendesa_idm (Sumber: kemendesa/idm)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_kemendesa_idm (
    id_kabupaten TEXT,
    provinsi TEXT,
    kabupaten_kota TEXT,
    total_desa BIGINT,
    total_kecamatan BIGINT,
    desa_mandiri BIGINT,
    desa_maju BIGINT,
    desa_berkembang BIGINT,
    desa_tertinggal BIGINT,
    desa_sangat_tertinggal BIGINT,
    indeks_ketahanan_sosial DOUBLE PRECISION,
    indeks_ketahanan_ekonomi DOUBLE PRECISION,
    indeks_ketahanan_lingkungan DOUBLE PRECISION,
    skor_idm DOUBLE PRECISION,
    status_idm TEXT,
    tahun BIGINT,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_kemendesa_idm IS 'kemendesa idm';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.id_kabupaten IS 'Kode wilayah administrasi kabupaten/kota (misal: 3302).';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.provinsi IS 'Nama provinsi wilayah administrasi.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.kabupaten_kota IS 'Nama kabupaten/kota wilayah administrasi.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.total_desa IS 'Total jumlah desa di wilayah kabupaten/kota.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.total_kecamatan IS 'Total jumlah kecamatan di wilayah kabupaten/kota.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.desa_mandiri IS 'Estimasi / jumlah desa berstatus Mandiri.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.desa_maju IS 'Estimasi / jumlah desa berstatus Maju.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.desa_berkembang IS 'Estimasi / jumlah desa berstatus Berkembang.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.desa_tertinggal IS 'Estimasi / jumlah desa berstatus Tertinggal.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.desa_sangat_tertinggal IS 'Estimasi / jumlah desa berstatus Sangat Tertinggal.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.indeks_ketahanan_sosial IS 'Rata-rata skor ketahanan sosial (IKS) desa.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.indeks_ketahanan_ekonomi IS 'Rata-rata skor ketahanan ekonomi (IKE) desa.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.indeks_ketahanan_lingkungan IS 'Rata-rata skor ketahanan ekologi/lingkungan (IKL) desa.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.skor_idm IS 'Skor komposit Indeks Desa Membangun (rata-rata IKS, IKE, IKL).';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.status_idm IS 'Klasifikasi status IDM wilayah (MANDIRI, MAJU, BERKEMBANG, TERTINGGAL, SANGAT TERTINGGAL).';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.tahun IS 'Tahun penilaian IDM.';
COMMENT ON COLUMN raw_kunker.raw_kemendesa_idm.data_source IS 'Sumber resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_kemenhub_hubud_bandara (Sumber: kemenhub/hubud_bandara)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_kemenhub_hubud_bandara (
    id_fasilitas TEXT,
    nama_fasilitas TEXT,
    jenis_infrastruktur TEXT,
    panjang_runway_m DOUBLE PRECISION,
    klasifikasi_pesawat_maks TEXT,
    kondisi_kemantapan_jalan_pct DOUBLE PRECISION,
    status_kelayakan_vvip TEXT,
    kode_icao TEXT,
    kode_iata TEXT,
    klasifikasi_icao TEXT,
    kekuatan_pcn TEXT,
    pengelola TEXT,
    alamat TEXT,
    jam_operasional TEXT,
    kabupaten_kota TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    elevasi_mdpl DOUBLE PRECISION,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_kemenhub_hubud_bandara IS 'kemenhub hubud_bandara';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.id_fasilitas IS 'Kode ICAO/IATA bandar udara atau ID fasilitas (misal: WIHH / HLP).';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.nama_fasilitas IS 'Nama resmi bandar udara atau pangkalan udara.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.jenis_infrastruktur IS 'Klasifikasi jenis bandara (Komersial, Militer/Pangkalan TNI AU, Enclave Sipil).';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.panjang_runway_m IS 'Panjang landasan pacu utama bandara dalam satuan meter.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.klasifikasi_pesawat_maks IS 'Tipe pesawat terbesar/kritis yang dapat dilayani landasan pacu.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.kondisi_kemantapan_jalan_pct IS 'Tingkat kemantapan dan kesiapan operasional perkerasan landasan (%)';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.status_kelayakan_vvip IS 'Rekomendasi teknis kesiapan protokoler/VVIP kepresidenan.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.kode_icao IS 'Kode 4 huruf International Civil Aviation Organization.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.kode_iata IS 'Kode 3 huruf International Air Transport Association.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.klasifikasi_icao IS 'Klasifikasi Aerodrome Reference Code ICAO (misal: 3C, 4D, 4E, 4F).';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.kekuatan_pcn IS 'Pavement Classification Number (PCN) kekuatan perkerasan landasan.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.pengelola IS 'Instansi / BUMN pengelola bandara (UPBU Kemenhub, PT Angkasa Pura, TNI AU).';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.alamat IS 'Alamat fisik lokasi bandara.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.jam_operasional IS 'Jam operasional penerbangan (misal: 24 Jam, 06.00-18.00 LT).';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.kabupaten_kota IS 'Wilayah administratif kabupaten/kota kedudukan bandara.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.latitude IS 'Koordinat lintang geografis.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.longitude IS 'Koordinat bujur geografis.';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.elevasi_mdpl IS 'Ketinggian bandara di atas permukaan laut (meter).';
COMMENT ON COLUMN raw_kunker.raw_kemenhub_hubud_bandara.data_source IS 'Sumber data resmi.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_kemenkes_satusehat_ckg (Sumber: kemenkes/satusehat_ckg)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_kemenkes_satusehat_ckg (
    id_fasyankes TEXT,
    nama_puskesmas_klinik TEXT,
    provinsi TEXT,
    kabupaten_kota TEXT,
    jumlah_skrining_balita BIGINT,
    jumlah_skrining_dewasa BIGINT,
    jumlah_skrining_lansia BIGINT,
    kasus_terindikasi_stunting BIGINT,
    kasus_dirujuk_ke_rs BIGINT,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_kemenkes_satusehat_ckg IS 'kemenkes satusehat_ckg';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_satusehat_ckg.id_fasyankes IS 'Kode registrasi fasyankes SATUSEHAT Kemenkes (contoh: P33020101).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_satusehat_ckg.nama_puskesmas_klinik IS 'Nama fasilitas pelayanan kesehatan pelaksana skrining CKG.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_satusehat_ckg.provinsi IS 'Provinsi lokasi fasyankes.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_satusehat_ckg.kabupaten_kota IS 'Kabupaten atau kota lokasi fasyankes.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_satusehat_ckg.jumlah_skrining_balita IS 'Jumlah balita yang telah diskrining tumbuh kembang (jiwa).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_satusehat_ckg.jumlah_skrining_dewasa IS 'Jumlah usia produktif yang diskrining penyakit tidak menular / PTM (jiwa).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_satusehat_ckg.jumlah_skrining_lansia IS 'Jumlah warga lansia yang diskrining kesehatan geriatri (jiwa).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_satusehat_ckg.kasus_terindikasi_stunting IS 'Jumlah balita yang terindikasi stunting atau wasting (kasus).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_satusehat_ckg.kasus_dirujuk_ke_rs IS 'Jumlah pasien yang memerlukan rujukan ke rumah sakit lanjutan (kasus).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_satusehat_ckg.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_kemenkes_siranap_rs_rujukan (Sumber: kemenkes/siranap_rs_rujukan)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_kemenkes_siranap_rs_rujukan (
    kode_rs TEXT,
    nama_rumah_sakit TEXT,
    kelas_rs TEXT,
    jarak_dari_lokasi_km DOUBLE PRECISION,
    waktu_tempuh_menit BIGINT,
    ketersediaan_icu_vvip BIGINT,
    bed_occupancy_rate_pct DOUBLE PRECISION,
    kesiapan_ambulans_vvip TEXT,
    alamat_rs TEXT,
    total_bed_kosong BIGINT,
    total_ruangan_terdata BIGINT,
    provinsi TEXT,
    kabupaten_kota TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_kemenkes_siranap_rs_rujukan IS 'kemenkes siranap_rs_rujukan';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.kode_rs IS 'Kode registrasi resmi Rumah Sakit Kementerian Kesehatan (misal: 3171012, 3302012).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.nama_rumah_sakit IS 'Nama resmi rumah sakit rujukan terdekat dari lokasi kunker.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.kelas_rs IS 'Tipe kelas RS (Kelas A Rujukan Utama/Nasional, Kelas B, Kelas C, RS TNI/Polri).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.jarak_dari_lokasi_km IS 'Estimasi jarak tempuh dari titik pusat kegiatan kunker (km).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.waktu_tempuh_menit IS 'Estimasi waktu tempuh iring-iringan darurat medis kepresidenan (menit).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.ketersediaan_icu_vvip IS 'Jumlah tempat tidur ICU/ICCU/VVIP/VIP siap pakai tanpa antrian.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.bed_occupancy_rate_pct IS 'Estimasi tingkat keterisian ranjang RS (Bed Occupancy Rate - BOR %).';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.kesiapan_ambulans_vvip IS 'Status kesiapan mini-ICU ambulans kepresidenan dan tim advance medis.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.alamat_rs IS 'Alamat fisik fasyankes rumah sakit.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.total_bed_kosong IS 'Total seluruh tempat tidur rawat inap yang kosong saat ini.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.total_ruangan_terdata IS 'Jumlah unit ruangan/kamar rawat inap terdata pada SIRANAP.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.provinsi IS 'Provinsi fasyankes rumah sakit.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.kabupaten_kota IS 'Kabupaten / Kota fasyankes rumah sakit.';
COMMENT ON COLUMN raw_kunker.raw_kemenkes_siranap_rs_rujukan.data_source IS 'Sumber data resmi penyedia ketersediaan tempat tidur rawat inap.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_kemenkop_simkopdes_kdmp (Sumber: kemenkop/simkopdes_kdmp)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_kemenkop_simkopdes_kdmp (
    provinsi TEXT,
    provinsi_id BIGINT,
    kabupaten_kota TEXT,
    total_koperasi BIGINT,
    koperasi_sehat BIGINT,
    koperasi_cukup_sehat BIGINT,
    koperasi_tidak_sehat BIGINT,
    total_anggota BIGINT,
    omzet_pendapatan DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_kemenkop_simkopdes_kdmp IS 'kemenkop simkopdes_kdmp';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.provinsi IS 'Nama provinsi wilayah kerja (misal: ''JAWA TIMUR'').';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.provinsi_id IS 'Kode ID provinsi Kemendagri / Simkopdes.';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.kabupaten_kota IS 'Nama kabupaten atau kota lokasi koperasi.';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.total_koperasi IS 'Jumlah unit Koperasi Desa Merah Putih terbentuk.';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.koperasi_sehat IS 'Jumlah koperasi berpredikat sehat.';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.koperasi_cukup_sehat IS 'Jumlah koperasi berpredikat cukup sehat.';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.koperasi_tidak_sehat IS 'Jumlah koperasi belum/tidak sehat.';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.total_anggota IS 'Total anggota masyarakat terdaftar.';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.omzet_pendapatan IS 'Akumulasi perputaran pendapatan koperasi dalam Rupiah.';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.latitude IS 'Titik koordinat lintang lokasi sentra koperasi.';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.longitude IS 'Titik koordinat bujur lokasi sentra koperasi.';
COMMENT ON COLUMN raw_kunker.raw_kemenkop_simkopdes_kdmp.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_kkp_kampung_nelayan_merah_putih (Sumber: kkp/kampung_nelayan_merah_putih)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_kkp_kampung_nelayan_merah_putih (
    id_knmp TEXT,
    nama_desa_nelayan TEXT,
    provinsi TEXT,
    kabupaten_kota TEXT,
    jumlah_nelayan BIGINT,
    kapasitas_cold_storage_ton DOUBLE PRECISION,
    produksi_es_ton_hari DOUBLE PRECISION,
    status_operasional TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_kkp_kampung_nelayan_merah_putih IS 'kkp kampung_nelayan_merah_putih';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.id_knmp IS 'Identifier unik sentra Kampung Nelayan Merah Putih (misal: ''KNMP-3301-01'').';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.nama_desa_nelayan IS 'Nama sentra perikanan, pelabuhan, atau kampung nelayan binaan.';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.provinsi IS 'Provinsi lokasi pesisir.';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.kabupaten_kota IS 'Kabupaten atau kota pesisir.';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.jumlah_nelayan IS 'Jumlah nelayan binaan aktif terdata di sentra perikanan.';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.kapasitas_cold_storage_ton IS 'Kapasitas fasilitas cold storage atau ruang pendingin ikan dalam satuan ton.';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.produksi_es_ton_hari IS 'Kapasitas produksi pabrik es penunjang mutu hasil tangkapan dalam ton/hari.';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.status_operasional IS 'Status operasional fasilitas sentra (misal: ''Beroperasi'', ''Pengembangan'', ''Persiapan'').';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.latitude IS 'Koordinat lintang lokasi geografis.';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.longitude IS 'Koordinat bujur lokasi geografis.';
COMMENT ON COLUMN raw_kunker.raw_kkp_kampung_nelayan_merah_putih.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_lapor_aduan (Sumber: lapor/rekap_aduan_wilayah)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_lapor_aduan (
    id_aduan TEXT,
    tanggal_lapor TEXT,
    kategori_program TEXT,
    provinsi TEXT,
    kabupaten_kota TEXT,
    uraian_laporan TEXT,
    status_tindak_lanjut TEXT,
    instansi_tujuan TEXT,
    jumlah_aduan BIGINT,
    tahun BIGINT,
    kode_wilayah TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_lapor_aduan IS 'lapor rekap_aduan_wilayah';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.id_aduan IS 'Nomor tiket aduan masyarakat atau kode agregat wilayah SP4N-LAPOR (misal: ADU-2024-8812 / LAPOR-3171-2024).';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.tanggal_lapor IS 'Waktu penyampaian laporan masyarakat (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.kategori_program IS 'Program terkait aduan (Pelayanan Publik, MBG, KDMP, Bansos, Infrastruktur, Pendidikan, Kesehatan).';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.provinsi IS 'Nama provinsi asal aduan/pelapor.';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.kabupaten_kota IS 'Nama kabupaten/kota asal aduan masyarakat.';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.uraian_laporan IS 'Ringkasan substansi keluhan, aspirasi, atau rekapitulasi pengaduan masyarakat.';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.status_tindak_lanjut IS 'Status progres tindak lanjut (Diverifikasi, Ditindaklanjuti, Selesai).';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.instansi_tujuan IS 'K/L atau Pemerintah Daerah penanggung jawab penyelesaian aduan.';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.jumlah_aduan IS 'Total volume aduan yang tercatat pada wilayah/periode terkait.';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.tahun IS 'Tahun periode pelaporan.';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.kode_wilayah IS 'Kode administrasi wilayah adm2 BPS/Kemendagri (misal: 31.71).';
COMMENT ON COLUMN raw_kunker.raw_lapor_aduan.data_source IS 'Sumber resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_setkab_matriks_janji_presiden (Sumber: setkab/matriks_janji_presiden)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_setkab_matriks_janji_presiden (
    id_komitmen TEXT,
    program_strategis TEXT,
    substansi_komitmen TEXT,
    tanggal_penyampaian TEXT,
    forum_agenda TEXT,
    provinsi TEXT,
    kabupaten_kota TEXT,
    desa_lokasi TEXT,
    kl_penanggung_jawab TEXT,
    status_pemenuhan TEXT,
    catatan_progres_sekdukkab TEXT,
    koordinasi_kemenko TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_setkab_matriks_janji_presiden IS 'setkab matriks_janji_presiden';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.id_komitmen IS 'Identifier resmi komitmen janji/arahan Presiden (misal: ''JNJ-2026-001'').';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.program_strategis IS 'Rumpun program atau sektor strategis prioritas Presiden.';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.substansi_komitmen IS 'Uraian isi komitmen atau arahan kerja spesifik Presiden.';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.tanggal_penyampaian IS 'Tanggal penyampaian komitmen/arahan (format: ''YYYY-MM-DD'' atau deskriptif).';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.forum_agenda IS 'Konteks seremonial kunjungan, rapat terbatas, atau forum kenegaraan.';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.provinsi IS 'Provinsi sasaran program atau lokasi kunjungan.';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.kabupaten_kota IS 'Kabupaten/Kota target penerima manfaat.';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.desa_lokasi IS 'Lokasi titik desa/kawasan fisik peninjauan proyek.';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.kl_penanggung_jawab IS 'Kementerian / Lembaga pengampu eksekusi program.';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.status_pemenuhan IS 'Status pelaksanaan komitmen (misal: ''Selesai'', ''On Progress'', ''Terkendala'').';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.catatan_progres_sekdukkab IS 'Catatan perkembangan monitoring Tim Dukungan Kerja Kabinet (Sekdukkab).';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.koordinasi_kemenko IS 'Kementerian Koordinator pembina penyelesaian komitmen.';
COMMENT ON COLUMN raw_kunker.raw_setkab_matriks_janji_presiden.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_setkab_tracking_arahan_lapangan (Sumber: setkab/tracking_arahan_lapangan)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_setkab_tracking_arahan_lapangan (
    id_arahan TEXT,
    tanggal_arahan TEXT,
    lokasi_kunjungan TEXT,
    isi_arahan_presiden TEXT,
    instansi_pelaksana TEXT,
    dokumen_dasar_tindak_lanjut TEXT,
    status_tindak_lanjut TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_setkab_tracking_arahan_lapangan IS 'setkab tracking_arahan_lapangan';
COMMENT ON COLUMN raw_kunker.raw_setkab_tracking_arahan_lapangan.id_arahan IS 'Nomor registrasi arahan kerja lapangan (misal: ''ARH-2026-041'').';
COMMENT ON COLUMN raw_kunker.raw_setkab_tracking_arahan_lapangan.tanggal_arahan IS 'Waktu penyampaian arahan saat kunjungan (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_kunker.raw_setkab_tracking_arahan_lapangan.lokasi_kunjungan IS 'Titik lokasi atau kabupaten/kota penyampaian instruksi presiden.';
COMMENT ON COLUMN raw_kunker.raw_setkab_tracking_arahan_lapangan.isi_arahan_presiden IS 'Petunjuk teknis atau instruksi Presiden kepada kementerian/lembaga atau kepala daerah.';
COMMENT ON COLUMN raw_kunker.raw_setkab_tracking_arahan_lapangan.instansi_pelaksana IS 'Instansi teknis kementerian/lembaga/pemda pengampu pelaksanaan tindak lanjut.';
COMMENT ON COLUMN raw_kunker.raw_setkab_tracking_arahan_lapangan.dokumen_dasar_tindak_lanjut IS 'Surat edaran, perpres, atau keputusan menteri penindak lanjut (misal: ''Kepmentan No. 241/2026'').';
COMMENT ON COLUMN raw_kunker.raw_setkab_tracking_arahan_lapangan.status_tindak_lanjut IS 'Status pelaksanaan tindak lanjut (Tercapai, Sedang Berjalan, Perlu Koordinasi).';
COMMENT ON COLUMN raw_kunker.raw_setkab_tracking_arahan_lapangan.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_setpres_matriks_risiko_kunjungan (Sumber: setpres/matriks_risiko_kunjungan)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_setpres_matriks_risiko_kunjungan (
    id_risiko TEXT,
    kategori_risiko TEXT,
    deskripsi_ancaman TEXT,
    tingkat_probabilitas TEXT,
    tingkat_dampak TEXT,
    rencana_mitigasi TEXT,
    penanggung_jawab_pic TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_setpres_matriks_risiko_kunjungan IS 'setpres matriks_risiko_kunjungan';
COMMENT ON COLUMN raw_kunker.raw_setpres_matriks_risiko_kunjungan.id_risiko IS 'Nomor register analisis risiko kunker (misal: ''RSK-2026-01'').';
COMMENT ON COLUMN raw_kunker.raw_setpres_matriks_risiko_kunjungan.kategori_risiko IS 'Kategori risiko (Protokoler, Medis, Cuaca, Kerawanan Massa, Aksesibilitas).';
COMMENT ON COLUMN raw_kunker.raw_setpres_matriks_risiko_kunjungan.deskripsi_ancaman IS 'Potensi kendala atau gangguan yang teridentifikasi di lokasi kunjungan.';
COMMENT ON COLUMN raw_kunker.raw_setpres_matriks_risiko_kunjungan.tingkat_probabilitas IS 'Tingkat peluang terjadinya kendala (Tinggi, Sedang, Rendah).';
COMMENT ON COLUMN raw_kunker.raw_setpres_matriks_risiko_kunjungan.tingkat_dampak IS 'Dampak terhadap kelancaran acara kepresidenan (Kritis, Signifikan, Minor).';
COMMENT ON COLUMN raw_kunker.raw_setpres_matriks_risiko_kunjungan.rencana_mitigasi IS 'Langkah antisipasi dan skenario cadangan (Plan B).';
COMMENT ON COLUMN raw_kunker.raw_setpres_matriks_risiko_kunjungan.penanggung_jawab_pic IS 'Satgas pengampu pelaksanaan mitigasi (Paspampres, Protokol Setpres, Dinkes, Kodim).';
COMMENT ON COLUMN raw_kunker.raw_setpres_matriks_risiko_kunjungan.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_kunker.raw_setpres_statistik_kunjungan_presiden (Sumber: setpres/statistik_kunjungan_presiden)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_kunker.raw_setpres_statistik_kunjungan_presiden (
    provinsi TEXT,
    kabupaten_kota TEXT,
    frekuensi_kunjungan_total BIGINT,
    kunjungan_terakhir TEXT,
    agenda_utama TEXT,
    durasi_kunjungan_hari BIGINT,
    pejabat_pendamping_utama TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_kunker.raw_setpres_statistik_kunjungan_presiden IS 'setpres statistik_kunjungan_presiden';
COMMENT ON COLUMN raw_kunker.raw_setpres_statistik_kunjungan_presiden.provinsi IS 'Nama provinsi wilayah kerja tempat kunjungan Presiden berlangsung.';
COMMENT ON COLUMN raw_kunker.raw_setpres_statistik_kunjungan_presiden.kabupaten_kota IS 'Nama kabupaten atau kota tempat pelaksanaan kunjungan Presiden.';
COMMENT ON COLUMN raw_kunker.raw_setpres_statistik_kunjungan_presiden.frekuensi_kunjungan_total IS 'Jumlah frekuensi kumulatif kunjungan kerja Presiden ke daerah bersangkutan.';
COMMENT ON COLUMN raw_kunker.raw_setpres_statistik_kunjungan_presiden.kunjungan_terakhir IS 'Waktu atau tanggal pelaksanaan rangkaian kunjungan kerja terbaru (format: ''YYYY-MM-DD'' atau deskriptif).';
COMMENT ON COLUMN raw_kunker.raw_setpres_statistik_kunjungan_presiden.agenda_utama IS 'Fokus agenda utama kegiatan Presiden (misal: peresmian infrastruktur, peninjauan pangan, bansos).';
COMMENT ON COLUMN raw_kunker.raw_setpres_statistik_kunjungan_presiden.durasi_kunjungan_hari IS 'Durasi pelaksanaan rangkaian kunjungan kerja dalam satuan hari.';
COMMENT ON COLUMN raw_kunker.raw_setpres_statistik_kunjungan_presiden.pejabat_pendamping_utama IS 'Daftar menteri, pejabat tinggi negara, atau pimpinan lembaga pendamping Presiden.';
COMMENT ON COLUMN raw_kunker.raw_setpres_statistik_kunjungan_presiden.data_source IS 'Lembaga penerbit resmi data.';

-- ========================================================
-- USECASE: GEOPOLITIK (Schema: raw_geopolitik)
-- ========================================================
CREATE SCHEMA IF NOT EXISTS raw_geopolitik;

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_airnav_notam (Sumber: airnav/notam)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_airnav_notam (
    id_wilayah TEXT,
    negara TEXT,
    kawasan TEXT,
    status_siaga_evakuasi TEXT,
    estimasi_wni_terdampak BIGINT,
    jalur_evakuasi_utama TEXT,
    titik_kumpul_safe_haven TEXT,
    status_ruang_udara_notam TEXT,
    kesiapan_bandara_pelabuhan TEXT,
    koordinasi_satgas_tni_kemlu TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_airnav_notam IS 'airnav notam';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.id_wilayah IS 'Identifier rencana kontinjensi wilayah (misal: ''EVAC-2026-ME-01'').';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.negara IS 'Negara lokasi kontinjensi krisis atau zona konflik.';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.kawasan IS 'Kawasan geopolitik internasional.';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.status_siaga_evakuasi IS 'Tingkat siaga kedaruratan (Siaga I, Siaga II, Siaga III).';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.estimasi_wni_terdampak IS 'Jumlah estimasi WNI terdata di zona bahaya.';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.jalur_evakuasi_utama IS 'Rute dan moda evakuasi (Jalur Udara, Koridor Darat, Konvoi Laut).';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.titik_kumpul_safe_haven IS 'Lokasi aman penampungan WNI sebelum evakuasi (KBRI, Safe Haven).';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.status_ruang_udara_notam IS 'Status NOTAM penerbangan (Open, Restricted, Closed).';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.kesiapan_bandara_pelabuhan IS 'Kondisi operasional fasilitas bandara/pelabuhan keberangkatan.';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.koordinasi_satgas_tni_kemlu IS 'Kesiapan koordinasi Satgas Gabungan TNI & Kemlu RI.';
COMMENT ON COLUMN raw_geopolitik.raw_airnav_notam.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_cekfakta_klarifikasi_hoaks (Sumber: cekfakta/klarifikasi_hoaks)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_cekfakta_klarifikasi_hoaks (
    id_narasi TEXT,
    isu_pemberitaan TEXT,
    klaim_narasi TEXT,
    asal_media_sumber TEXT,
    tingkat_sebaran TEXT,
    hasil_verifikasi_cek_fakta TEXT,
    tanggapan_resmi_pemerintah TEXT,
    instansi_klarifikasi TEXT,
    tanggal_klarifikasi TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_cekfakta_klarifikasi_hoaks IS 'cekfakta klarifikasi_hoaks';
COMMENT ON COLUMN raw_geopolitik.raw_cekfakta_klarifikasi_hoaks.id_narasi IS 'Identifier pemantauan narasi internasional (misal: ''NAR-2026-01'').';
COMMENT ON COLUMN raw_geopolitik.raw_cekfakta_klarifikasi_hoaks.isu_pemberitaan IS 'Isu atau topik pemberitaan geopolitik mengenai Indonesia.';
COMMENT ON COLUMN raw_geopolitik.raw_cekfakta_klarifikasi_hoaks.klaim_narasi IS 'Substansi narasi yang beredar di media massa internasional atau ruang publik.';
COMMENT ON COLUMN raw_geopolitik.raw_cekfakta_klarifikasi_hoaks.asal_media_sumber IS 'Media internasional atau platform media sosial asal narasi.';
COMMENT ON COLUMN raw_geopolitik.raw_cekfakta_klarifikasi_hoaks.tingkat_sebaran IS 'Tingkat persebaran isu (Tinggi / Viral, Sedang, Rendah).';
COMMENT ON COLUMN raw_geopolitik.raw_cekfakta_klarifikasi_hoaks.hasil_verifikasi_cek_fakta IS 'Hasil verifikasi fakta (Fakta, Misinformasi, Konteks Dimanipulasi, Disinformasi).';
COMMENT ON COLUMN raw_geopolitik.raw_cekfakta_klarifikasi_hoaks.tanggapan_resmi_pemerintah IS 'Substansi tanggapan dan klarifikasi resmi pemerintah.';
COMMENT ON COLUMN raw_geopolitik.raw_cekfakta_klarifikasi_hoaks.instansi_klarifikasi IS 'Instansi juru bicara pemerintah.';
COMMENT ON COLUMN raw_geopolitik.raw_cekfakta_klarifikasi_hoaks.tanggal_klarifikasi IS 'Waktu publikasi klarifikasi resmi (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_geopolitik.raw_cekfakta_klarifikasi_hoaks.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_csis_amti_insiden_maritim (Sumber: csis/amti_insiden_maritim)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_csis_amti_insiden_maritim (
    id_insiden TEXT,
    tanggal_kejadian TEXT,
    wilayah_perairan TEXT,
    jenis_kejadian TEXT,
    pihak_terlibat TEXT,
    koordinat_lat DOUBLE PRECISION,
    koordinat_lon DOUBLE PRECISION,
    tingkat_eskalasi TEXT,
    catatan_analisis TEXT,
    data_source TEXT,
    PRIMARY KEY (id_insiden)
);

COMMENT ON TABLE raw_geopolitik.raw_csis_amti_insiden_maritim IS 'csis amti_insiden_maritim';
COMMENT ON COLUMN raw_geopolitik.raw_csis_amti_insiden_maritim.id_insiden IS 'Identifier kejadian insiden maritim (misal: ''INS-AMTI-2026-08'').';
COMMENT ON COLUMN raw_geopolitik.raw_csis_amti_insiden_maritim.tanggal_kejadian IS 'Waktu kejadian berlangsung (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_geopolitik.raw_csis_amti_insiden_maritim.wilayah_perairan IS 'Kawasan perairan strategis (Laut China Selatan, Selat Malaka, Laut Natuna Utara, dll.).';
COMMENT ON COLUMN raw_geopolitik.raw_csis_amti_insiden_maritim.jenis_kejadian IS 'Jenis insiden maritim (Manuver Kapal Milisi, Latihan Tembak Amunisi Aktif, dll.).';
COMMENT ON COLUMN raw_geopolitik.raw_csis_amti_insiden_maritim.pihak_terlibat IS 'Negara atau angkatan laut/penjaga pantai yang terlibat.';
COMMENT ON COLUMN raw_geopolitik.raw_csis_amti_insiden_maritim.koordinat_lat IS 'Koordinat lintang insiden.';
COMMENT ON COLUMN raw_geopolitik.raw_csis_amti_insiden_maritim.koordinat_lon IS 'Koordinat bujur insiden.';
COMMENT ON COLUMN raw_geopolitik.raw_csis_amti_insiden_maritim.tingkat_eskalasi IS 'Tingkat eskalasi ketegangan (Tinggi, Sedang, Rendah).';
COMMENT ON COLUMN raw_geopolitik.raw_csis_amti_insiden_maritim.catatan_analisis IS 'Catatan implikasi terhadap jalur pelayaran nasional dan keamanan maritim.';
COMMENT ON COLUMN raw_geopolitik.raw_csis_amti_insiden_maritim.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_esdm_harga_minyak_mentah_icp (Sumber: esdm/harga_minyak_mentah_icp)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_esdm_harga_minyak_mentah_icp (
    periode_data TEXT,
    tahun BIGINT,
    bulan TEXT,
    icp_usd DOUBLE PRECISION,
    icp_perubahan_usd DOUBLE PRECISION,
    brent_ice_usd DOUBLE PRECISION,
    wti_nymex_usd DOUBLE PRECISION,
    dated_brent_usd DOUBLE PRECISION,
    basket_opec_usd DOUBLE PRECISION,
    nomor_kepmen TEXT,
    faktor_geopolitik_pasar TEXT,
    sumber_dokumen_url TEXT,
    data_source TEXT,
    PRIMARY KEY (bulan, tahun)
);

COMMENT ON TABLE raw_geopolitik.raw_esdm_harga_minyak_mentah_icp IS 'esdm harga_minyak_mentah_icp';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.periode_data IS 'Periode bulan dan tahun penetapan (misal: ''2026-09'' atau ''September 2026'').';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.tahun IS 'Tahun kalender penetapan ICP (misal: 2026).';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.bulan IS 'Nama bulan kalender penetapan (misal: ''Januari'', ''Februari'', dst).';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.icp_usd IS 'Harga rata-rata Minyak Mentah Indonesia (Indonesian Crude Price / ICP) resmi dalam USD per barel.';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.icp_perubahan_usd IS 'Perubahan kenaikan atau penurunan ICP dibandingkan bulan sebelumnya dalam USD per barel.';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.brent_ice_usd IS 'Harga acuan minyak mentah Brent (ICE) rata-rata bulanan dalam USD per barel.';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.wti_nymex_usd IS 'Harga acuan minyak mentah West Texas Intermediate / WTI (Nymex) rata-rata bulanan dalam USD per barel.';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.dated_brent_usd IS 'Harga acuan Dated Brent rata-rata bulanan dalam USD per barel.';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.basket_opec_usd IS 'Harga acuan Basket OPEC rata-rata bulanan dalam USD per barel.';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.nomor_kepmen IS 'Nomor Keputusan Menteri ESDM RI tentang penetapan ICP bulan berkenaan.';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.faktor_geopolitik_pasar IS 'Ringkasan faktor geopolitik, rantai pasok energi global, dan dinamika pasar yang memengaruhi ICP.';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.sumber_dokumen_url IS 'Tautan resmi dokumen Kepmen atau publikasi berita siaran pers Kementerian ESDM RI.';
COMMENT ON COLUMN raw_geopolitik.raw_esdm_harga_minyak_mentah_icp.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_gdacs_kedaruratan_bencana (Sumber: gdacs/kedaruratan_bencana)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_gdacs_kedaruratan_bencana (
    id_peringatan TEXT,
    nama_kejadian TEXT,
    negara_kawasan TEXT,
    jenis_kedaruratan TEXT,
    level_waspada TEXT,
    tanggal_kejadian TEXT,
    estimasi_korban_terdampak BIGINT,
    potensi_imbas_ke_indonesia TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    severity TEXT,
    kode_event TEXT,
    deskripsi TEXT,
    link_detail TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_gdacs_kedaruratan_bencana IS 'gdacs kedaruratan_bencana';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.id_peringatan IS 'Identifier unik kedaruratan bencana internasional (misal: EQ1571367, TC1001337).';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.nama_kejadian IS 'Nama bencana alam atau kedaruratan kesehatan global.';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.negara_kawasan IS 'Negara atau wilayah geografis terdampak bencana.';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.jenis_kedaruratan IS 'Kategori bencana (Gempa Bumi, Siklon Tropis, Tsunami, Banjir, Letusan Gunung Api, Kebakaran Hutan).';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.level_waspada IS 'Status tingkat risiko resmi: Red Alert, Orange Alert, Green Alert.';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.tanggal_kejadian IS 'Waktu awal bencana terdeteksi dalam format ISO YYYY-MM-DD.';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.estimasi_korban_terdampak IS 'Estimasi jumlah populasi warga yang terdampak langsung (jiwa).';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.potensi_imbas_ke_indonesia IS 'Analisis potensi dampak terhadap keselamatan WNI di wilayah, jalur logistik pelayaran, atau pasokan impor pangan.';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.latitude IS 'Titik koordinat garis lintang pusat bencana.';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.longitude IS 'Titik koordinat garis bujur pusat bencana.';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.severity IS 'Tingkat keparahan parameter teknis bencana (magnitudo, kecepatan angin, luas area).';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.kode_event IS 'Kode tipe kejadian GDACS (EQ, TC, TS, FL, VO, WF, DR).';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.deskripsi IS 'Ringkasan narasi resmi kejadian bencana GDACS.';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.link_detail IS 'Tautan laporan analisis spasial bencana GDACS.';
COMMENT ON COLUMN raw_geopolitik.raw_gdacs_kedaruratan_bencana.data_source IS 'Sumber resmi data kedaruratan bencana global.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_gdelt_media_asing (Sumber: gdelt/media_asing)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_gdelt_media_asing (
    tanggal_artikel TEXT,
    judul_berita TEXT,
    nama_media_sumber TEXT,
    negara_asal_media TEXT,
    kawasan_media TEXT,
    topik_utama TEXT,
    skor_sentimen_gdelt DOUBLE PRECISION,
    url_artikel TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_gdelt_media_asing IS 'gdelt media_asing';
COMMENT ON COLUMN raw_geopolitik.raw_gdelt_media_asing.tanggal_artikel IS 'Waktu publikasi berita internasional (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_geopolitik.raw_gdelt_media_asing.judul_berita IS 'Judul artikel berita media asing tentang Indonesia.';
COMMENT ON COLUMN raw_geopolitik.raw_gdelt_media_asing.nama_media_sumber IS 'Nama kantor berita / media asing (Reuters, Bloomberg, Nikkei Asia, dll.).';
COMMENT ON COLUMN raw_geopolitik.raw_gdelt_media_asing.negara_asal_media IS 'Negara basis media penerbit.';
COMMENT ON COLUMN raw_geopolitik.raw_gdelt_media_asing.kawasan_media IS 'Kawasan asal media (Asia Pasifik, Amerika Utara, Eropa).';
COMMENT ON COLUMN raw_geopolitik.raw_gdelt_media_asing.topik_utama IS 'Kategori isu (Diplomasi & Geopolitik, Investasi & Nikel, Hankam).';
COMMENT ON COLUMN raw_geopolitik.raw_gdelt_media_asing.skor_sentimen_gdelt IS 'Skor tone sentimen algoritma GDELT (-10.0 s.d +10.0).';
COMMENT ON COLUMN raw_geopolitik.raw_gdelt_media_asing.url_artikel IS 'Tautan URL artikel berita daring asli.';
COMMENT ON COLUMN raw_geopolitik.raw_gdelt_media_asing.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_imf_chokepoints (Sumber: imf/chokepoints_maritim)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_imf_chokepoints (
    date TEXT,
    year BIGINT,
    month BIGINT,
    day BIGINT,
    portid TEXT,
    portname TEXT,
    n_container BIGINT,
    n_dry_bulk BIGINT,
    n_general_cargo BIGINT,
    n_roro BIGINT,
    n_tanker BIGINT,
    n_cargo BIGINT,
    n_total BIGINT,
    capacity_container DOUBLE PRECISION,
    capacity_dry_bulk DOUBLE PRECISION,
    capacity_general_cargo DOUBLE PRECISION,
    capacity_roro DOUBLE PRECISION,
    capacity_tanker DOUBLE PRECISION,
    capacity_cargo DOUBLE PRECISION,
    capacity DOUBLE PRECISION,
    object_id BIGINT,
    PRIMARY KEY (date)
);

COMMENT ON TABLE raw_geopolitik.raw_imf_chokepoints IS 'imf chokepoints_maritim';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.date IS 'Tanggal observasi harian (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.year IS 'Tahun observasi.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.month IS 'Bulan observasi.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.day IS 'Hari observasi.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.portid IS 'ID unik chokepoint PortWatch (misal: chokepoint1, chokepoint5).';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.portname IS 'Nama chokepoint (misal: Malacca Strait, Suez Canal, Bab el-Mandeb Strait).';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.n_container IS 'Jumlah lintasan kapal kontainer.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.n_dry_bulk IS 'Jumlah lintasan kapal dry bulk.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.n_general_cargo IS 'Jumlah lintasan kapal general cargo.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.n_roro IS 'Jumlah lintasan kapal ro-ro.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.n_tanker IS 'Jumlah lintasan kapal tanker minyak/gas.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.n_cargo IS 'Jumlah lintasan seluruh kapal kargo.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.n_total IS 'Total seluruh lintasan kapal pada titik chokepoint.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.capacity_container IS 'Kapasitas muatan kapal kontainer (TEU).';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.capacity_dry_bulk IS 'Kapasitas muatan dry bulk (DWT).';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.capacity_general_cargo IS 'Kapasitas muatan general cargo (DWT).';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.capacity_roro IS 'Kapasitas kapal ro-ro.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.capacity_tanker IS 'Kapasitas muatan tanker (DWT).';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.capacity_cargo IS 'Kapasitas muatan kargo total.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.capacity IS 'Akumulasi kapasitas total lintasan kapal.';
COMMENT ON COLUMN raw_geopolitik.raw_imf_chokepoints.object_id IS 'ID internal objek ArcGIS Server.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_kemlu_iuran_organisasi_internasional (Sumber: kemlu/iuran_organisasi_internasional)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_kemlu_iuran_organisasi_internasional (
    id_organisasi TEXT,
    nama_organisasi_internasional TEXT,
    kategori_oi TEXT,
    dasar_hukum_keanggotaan TEXT,
    kl_focal_point TEXT,
    besaran_iuran_tahunan_valas DOUBLE PRECISION,
    mata_uang TEXT,
    ekuivalen_rupiah_miliar DOUBLE PRECISION,
    evaluasi_kemanfaatan TEXT,
    status_iuran_terakhir TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_kemlu_iuran_organisasi_internasional IS 'kemlu iuran_organisasi_internasional';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.id_organisasi IS 'Kode registrasi keanggotaan OI Kemenlu (misal: ''OI-UN-001'').';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.nama_organisasi_internasional IS 'Nama Organisasi Internasional (OI).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.kategori_oi IS 'Kategori (PBB & Badan Khusus, Kerja Sama Kawasan, Lembaga Keuangan, Komoditas).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.dasar_hukum_keanggotaan IS 'Dasar ratifikasi / keanggotaan (Keppres/Perpres).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.kl_focal_point IS 'Kementerian teknis pemegang mandat focal point RI.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.besaran_iuran_tahunan_valas IS 'Nominal tagihan kontribusi keanggotaan.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.mata_uang IS 'Mata uang pembayaran (USD, CHF, EUR, GBP).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.ekuivalen_rupiah_miliar IS 'Estimasi alokasi APBN untuk pembayaran iuran (Miliar Rupiah).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.evaluasi_kemanfaatan IS 'Hasil evaluasi berkala kemanfaatan bagi kepentingan nasional RI.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.status_iuran_terakhir IS 'Status pembayaran tahun berjalan (Lunas, Proses Pencairan, Tertunda).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_iuran_organisasi_internasional.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_kemlu_kasus_wni (Sumber: kemlu/kasus_wni)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_kemlu_kasus_wni (
    id_kasus TEXT,
    negara_kejadian TEXT,
    kategori_kasus TEXT,
    jumlah_korban_terlibat BIGINT,
    tanggal_pengaduan TEXT,
    status_penanganan TEXT,
    bantuan_hukum_diberikan TEXT,
    data_source TEXT,
    PRIMARY KEY (id_kasus)
);

COMMENT ON TABLE raw_geopolitik.raw_kemlu_kasus_wni IS 'kemlu kasus_wni';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_kasus_wni.id_kasus IS 'Nomor registrasi/tiket kasus pelindungan WNI (misal: ''PWNI-2026-MY-412'').';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_kasus_wni.negara_kejadian IS 'Negara tempat timbulnya kasus hukum, ketenagakerjaan, atau keimigrasian.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_kasus_wni.kategori_kasus IS 'Kategori kasus (Gaji Tidak Dibayar, Keimigrasian, TPPO / Online Scam, dsb).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_kasus_wni.jumlah_korban_terlibat IS 'Jumlah estimasi WNI korban atau pihak terkait.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_kasus_wni.tanggal_pengaduan IS 'Waktu tanggal laporan diterima perwakilan RI (format: ''YYYY-MM-DD'').';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_kasus_wni.status_penanganan IS 'Status penanganan kasus (Dalam Proses, Mediasi Selesai, Repatriasi Selesai).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_kasus_wni.bantuan_hukum_diberikan IS 'Bentuk advokasi diplomatik, pendampingan hukum retainer, atau safe house.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_kasus_wni.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_kemlu_safe_travel (Sumber: kemlu/safe_travel)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_kemlu_safe_travel (
    negara TEXT,
    kawasan TEXT,
    level_peringatan TEXT,
    ringkasan_imbauan TEXT,
    tanggal_rilis TEXT,
    pemicu_peringatan TEXT,
    nomor_hotline_kbri_kjri TEXT,
    news_id TEXT,
    uuid TEXT,
    news_title TEXT,
    news_info TEXT,
    news_image_path TEXT,
    news_total_read BIGINT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_kemlu_safe_travel IS 'kemlu safe_travel';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.negara IS 'Negara tujuan perjalanan yang menjadi sasaran imbauan resmi.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.kawasan IS 'Kawasan geografis negara tujuan (misal: Asia Tenggara, Timur Tengah, Eropa).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.level_peringatan IS 'Tingkat keamanan: Level 1 Aman, Level 2 Waspada, Level 3 Hati-hati, Level 4 Bahaya.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.ringkasan_imbauan IS 'Substansi imbauan resmi bagi WNI.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.tanggal_rilis IS 'Waktu publikasi imbauan (format ISO YYYY-MM-DD).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.pemicu_peringatan IS 'Penyebab eskalasi risiko (Konflik Bersenjata, Bencana Alam, Kerusuhan, Wabah, Regulasi).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.nomor_hotline_kbri_kjri IS 'Nomor hotline darurat perwakilan RI setempat (KBRI/KJRI).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.news_id IS 'ID unik berita imbauan dari portal Safe Travel.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.uuid IS 'UUID record Safe Travel Kemlu.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.news_title IS 'Judul lengkap siaran imbauan perjalanan.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.news_info IS 'Kategori informasi internal Kemlu (Keamanan, Keimigrasian, Kesehatan, dsb).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.news_image_path IS 'Tautan gambar atau poster imbauan resmi.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.news_total_read IS 'Jumlah pembaca siaran imbauan.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_safe_travel.data_source IS 'Sumber data resmi penyedia imbauan.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_kemlu_sebaran_wni_pmi (Sumber: kemlu/sebaran_wni_pmi)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_kemlu_sebaran_wni_pmi (
    negara TEXT,
    kawasan TEXT,
    jumlah_wni_lapor_diri BIGINT,
    pekerja_migran_pmi BIGINT,
    pelajar_mahasiswa BIGINT,
    staf_profesional_ekspat BIGINT,
    perwakilan_ri_pengampu TEXT,
    data_source TEXT,
    PRIMARY KEY (negara)
);

COMMENT ON TABLE raw_geopolitik.raw_kemlu_sebaran_wni_pmi IS 'kemlu sebaran_wni_pmi';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_sebaran_wni_pmi.negara IS 'Negara tempat tinggal atau penempatan WNI/PMI.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_sebaran_wni_pmi.kawasan IS 'Kawasan geografis penempatan diplomatik (misal: ''Asia Tenggara'', ''Timur Tengah'', ''Amerika Utara'').';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_sebaran_wni_pmi.jumlah_wni_lapor_diri IS 'Total akumulasi WNI yang aktif melakukan lapor diri pada Portal Peduli WNI.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_sebaran_wni_pmi.pekerja_migran_pmi IS 'Jumlah estimasi Pekerja Migran Indonesia (PMI) resmi terdaftar.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_sebaran_wni_pmi.pelajar_mahasiswa IS 'Jumlah pelajar dan mahasiswa Indonesia di negara bersangkutan.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_sebaran_wni_pmi.staf_profesional_ekspat IS 'Jumlah staf profesional, diaspora, atau ekspatriat Indonesia.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_sebaran_wni_pmi.perwakilan_ri_pengampu IS 'Nama KBRI / KJRI / KRI yang membawahi wilayah hukum penempatan.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_sebaran_wni_pmi.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_kemlu_treaty_room (Sumber: kemlu/treaty_room)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_kemlu_treaty_room (
    id_perjanjian TEXT,
    negara_mitra TEXT,
    judul_perjanjian TEXT,
    bidang_kerja_sama TEXT,
    tahapan TEXT,
    tanggal_penandatanganan TEXT,
    dasar_pengesahan_uu_perpres TEXT,
    instansi_penanggung_jawab_kl TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_kemlu_treaty_room IS 'kemlu treaty_room';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_treaty_room.id_perjanjian IS 'Nomor registrasi traktat internasional Kemenlu (misal: ''TR-2026-US-04'').';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_treaty_room.negara_mitra IS 'Negara pihak lawan perjanjian kerja sama bilateral.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_treaty_room.judul_perjanjian IS 'Judul resmi naskah perjanjian internasional (PI).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_treaty_room.bidang_kerja_sama IS 'Bidang kerja sama (Hankam, Ekonomi & Energi, Maritim, Pendidikan, Kesehatan).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_treaty_room.tahapan IS 'Tahap perkembangan traktat (Negosiasi, Ditandatangani, Diratifikasi, Dilaksanakan).';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_treaty_room.tanggal_penandatanganan IS 'Waktu penandatanganan traktat (format: ''YYYY-MM-DD'').';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_treaty_room.dasar_pengesahan_uu_perpres IS 'Nomor regulasi UU atau Perpres pengesahan ratifikasi traktat.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_treaty_room.instansi_penanggung_jawab_kl IS 'Kementerian / Lembaga teknis pengampu eksekusi kerja sama bilateral.';
COMMENT ON COLUMN raw_geopolitik.raw_kemlu_treaty_room.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_ofac_sanksi_perdagangan (Sumber: ofac/sanksi_perdagangan)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_ofac_sanksi_perdagangan (
    id_sanksi TEXT,
    otoritas_penerbit TEXT,
    negara_sasaran TEXT,
    sektor_terkena TEXT,
    tanggal_efektif TEXT,
    komoditas_terdampak_indonesia TEXT,
    potensi_dampak_ke_pelaku_usaha TEXT,
    nama_entitas TEXT,
    tipe_entitas TEXT,
    program_sanksi TEXT,
    catatan_sanksi TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_ofac_sanksi_perdagangan IS 'ofac sanksi_perdagangan';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.id_sanksi IS 'Identifier resmi regulasi sanksi perdagangan dan embargo (misal: OFAC-SDN-36, SNK-OFAC-2026-12).';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.otoritas_penerbit IS 'Otoritas penerbit sanksi internasional (US OFAC, European Union, UN Security Council).';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.negara_sasaran IS 'Negara sasaran sanksi, embargo ekonomi, atau pembatasan dagang.';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.sektor_terkena IS 'Sektor ekonomi sasaran (Perbankan & Keuangan, Energi & Minyak, Logistik Maritim, Teknologi).';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.tanggal_efektif IS 'Waktu mulai berlakunya pembatasan dalam format ISO YYYY-MM-DD.';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.komoditas_terdampak_indonesia IS 'Komoditas atau produk ekspor-impor Indonesia yang rawan terimbas sanksi.';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.potensi_dampak_ke_pelaku_usaha IS 'Analisis risiko sanksi sekunder bagi eksportir, importir, dan perbankan devisa nasional.';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.nama_entitas IS 'Nama resmi badan usaha, institusi, kapal, atau individu yang masuk dalam daftar sanksi SDN.';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.tipe_entitas IS 'Klasifikasi subjek sanksi: Individual, Entity/Corporate, Vessel, Aircraft.';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.program_sanksi IS 'Kode program sanksi resmi OFAC (misal: RUSSIA-EO14024, CUBA, IRAN, SDGT).';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.catatan_sanksi IS 'Keterangan tambahan identifikasi entitas (alias, IMO number, alamat).';
COMMENT ON COLUMN raw_geopolitik.raw_ofac_sanksi_perdagangan.data_source IS 'Sumber resmi daftar sanksi SDN OFAC.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_setpres_pertemuan_bilateral (Sumber: setpres/pertemuan_bilateral)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_setpres_pertemuan_bilateral (
    id_pertemuan TEXT,
    tanggal_kegiatan TEXT,
    negara_mitra TEXT,
    lokasi_kota_negara TEXT,
    format_pertemuan TEXT,
    tokoh_pemimpin_mitra TEXT,
    isu_utama_dibahas TEXT,
    kesepakatan_konkret TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_setpres_pertemuan_bilateral IS 'setpres pertemuan_bilateral';
COMMENT ON COLUMN raw_geopolitik.raw_setpres_pertemuan_bilateral.id_pertemuan IS 'Kode registrasi pertemuan diplomatik (misal: ''BIL-2026-01'').';
COMMENT ON COLUMN raw_geopolitik.raw_setpres_pertemuan_bilateral.tanggal_kegiatan IS 'Waktu pertemuan berlangsung (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_geopolitik.raw_setpres_pertemuan_bilateral.negara_mitra IS 'Negara mitra pertemuan diplomatik.';
COMMENT ON COLUMN raw_geopolitik.raw_setpres_pertemuan_bilateral.lokasi_kota_negara IS 'Tempat terselenggaranya pertemuan (misal: ''Istana Singapura'', ''Canberra, Australia'').';
COMMENT ON COLUMN raw_geopolitik.raw_setpres_pertemuan_bilateral.format_pertemuan IS 'Format (Kunjungan Kenegaraan, KTT Bilateral, Pertemuan Bilateral Sela-sela).';
COMMENT ON COLUMN raw_geopolitik.raw_setpres_pertemuan_bilateral.tokoh_pemimpin_mitra IS 'Nama Presiden / Perdana Menteri / Kepala Negara mitra.';
COMMENT ON COLUMN raw_geopolitik.raw_setpres_pertemuan_bilateral.isu_utama_dibahas IS 'Fokus substansi bahasan diplomatik (Investasi EBT, Kerja Sama Hankam, IKN).';
COMMENT ON COLUMN raw_geopolitik.raw_setpres_pertemuan_bilateral.kesepakatan_konkret IS 'Hasil deliverables atau dokumen kerja sama yang disepakati.';
COMMENT ON COLUMN raw_geopolitik.raw_setpres_pertemuan_bilateral.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_sipri_belanja_militer (Sumber: sipri/belanja_militer)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_sipri_belanja_militer (
    negara TEXT,
    tahun BIGINT,
    belanja_militer_juta_usd DOUBLE PRECISION,
    belanja_militer_pct_pdb DOUBLE PRECISION,
    belanja_militer_pct_apbn DOUBLE PRECISION,
    peringkat_belanja_dunia BIGINT,
    tren_modernisasi_alutsista TEXT,
    kawasan TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_sipri_belanja_militer IS 'sipri belanja_militer';
COMMENT ON COLUMN raw_geopolitik.raw_sipri_belanja_militer.negara IS 'Nama negara mitra diplomatik atau negara tetangga kawasan (misal: Indonesia, Singapura, Australia, China).';
COMMENT ON COLUMN raw_geopolitik.raw_sipri_belanja_militer.tahun IS 'Tahun anggaran pertahanan dan belanja militer (misal: 2024, 2023).';
COMMENT ON COLUMN raw_geopolitik.raw_sipri_belanja_militer.belanja_militer_juta_usd IS 'Total pengeluaran militer dalam satuan Juta US Dollar (Current Prices).';
COMMENT ON COLUMN raw_geopolitik.raw_sipri_belanja_militer.belanja_militer_pct_pdb IS 'Porsi pengeluaran militer terhadap Produk Domestik Bruto / PDB (%).';
COMMENT ON COLUMN raw_geopolitik.raw_sipri_belanja_militer.belanja_militer_pct_apbn IS 'Porsi belanja militer terhadap total belanja pemerintah / APBN (%).';
COMMENT ON COLUMN raw_geopolitik.raw_sipri_belanja_militer.peringkat_belanja_dunia IS 'Estimasi peringkat besaran belanja militer global pada tahun anggaran terkait.';
COMMENT ON COLUMN raw_geopolitik.raw_sipri_belanja_militer.tren_modernisasi_alutsista IS 'Fokus pengadaan alutsista strategis (Armada Laut, Rudal Jarak Jauh, Jet Tempur, dsb).';
COMMENT ON COLUMN raw_geopolitik.raw_sipri_belanja_militer.kawasan IS 'Kawasan geografis negara bersangkutan (Asia Tenggara, Asia Timur, Oseania, dll).';
COMMENT ON COLUMN raw_geopolitik.raw_sipri_belanja_militer.data_source IS 'Sumber resmi database belanja militer global SIPRI.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_ucdp_konflik_global (Sumber: ucdp/konflik_global)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_ucdp_konflik_global (
    id_konflik TEXT,
    negara TEXT,
    kawasan TEXT,
    aktor_terlibat TEXT,
    jenis_konflik TEXT,
    tanggal_kejadian TEXT,
    jumlah_korban_tewas BIGINT,
    koordinat_lat DOUBLE PRECISION,
    koordinat_lon DOUBLE PRECISION,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_ucdp_konflik_global IS 'ucdp konflik_global';
COMMENT ON COLUMN raw_geopolitik.raw_ucdp_konflik_global.id_konflik IS 'Identifier insiden konflik bersenjata resmi UCDP (misal: ''UCDP-2026-091'' atau relid).';
COMMENT ON COLUMN raw_geopolitik.raw_ucdp_konflik_global.negara IS 'Negara lokasi bentrokan bersenjata.';
COMMENT ON COLUMN raw_geopolitik.raw_ucdp_konflik_global.kawasan IS 'Kawasan geografis konflik (misal: ''Eropa Timur'', ''Afrika Utara'', ''Asia'').';
COMMENT ON COLUMN raw_geopolitik.raw_ucdp_konflik_global.aktor_terlibat IS 'Pihak aktor yang bertikai (Pemerintah vs Pemberontak / Milisi / Sipil).';
COMMENT ON COLUMN raw_geopolitik.raw_ucdp_konflik_global.jenis_konflik IS 'Kategori kekerasan bersenjata (State-based, Non-state conflict, One-sided violence).';
COMMENT ON COLUMN raw_geopolitik.raw_ucdp_konflik_global.tanggal_kejadian IS 'Waktu insiden tanggal kejadian konflik (format: ''YYYY-MM-DD'').';
COMMENT ON COLUMN raw_geopolitik.raw_ucdp_konflik_global.jumlah_korban_tewas IS 'Jumlah korban jiwa terverifikasi (best estimate fatalities).';
COMMENT ON COLUMN raw_geopolitik.raw_ucdp_konflik_global.koordinat_lat IS 'Titik koordinat lintang lokasi bentrokan.';
COMMENT ON COLUMN raw_geopolitik.raw_ucdp_konflik_global.koordinat_lon IS 'Titik koordinat bujur lokasi bentrokan.';
COMMENT ON COLUMN raw_geopolitik.raw_ucdp_konflik_global.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_un_comtrade (Sumber: un/comtrade)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_un_comtrade (
    periode_bulan TEXT,
    kode_hs_2digit TEXT,
    deskripsi_komoditas TEXT,
    arus_perdagangan TEXT,
    negara_mitra_utama TEXT,
    volume_ribu_ton DOUBLE PRECISION,
    nilai_fob_cif_juta_usd DOUBLE PRECISION,
    pertumbuhan_tahunan_pct DOUBLE PRECISION,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_un_comtrade IS 'un comtrade';
COMMENT ON COLUMN raw_geopolitik.raw_un_comtrade.periode_bulan IS 'Periode bulan transaksi perdagangan luar negeri (format YYYY-MM).';
COMMENT ON COLUMN raw_geopolitik.raw_un_comtrade.kode_hs_2digit IS 'Klasifikasi 2 digit HS Code (contoh: 75, 10, 15, 27, 85).';
COMMENT ON COLUMN raw_geopolitik.raw_un_comtrade.deskripsi_komoditas IS 'Nama kelompok produk strategis (Nikel Smelter, Gandum, CPO, Batubara, Semikonduktor).';
COMMENT ON COLUMN raw_geopolitik.raw_un_comtrade.arus_perdagangan IS 'Arus barang: Ekspor atau Impor.';
COMMENT ON COLUMN raw_geopolitik.raw_un_comtrade.negara_mitra_utama IS 'Negara asal impor atau tujuan ekspor terbesar (Tiongkok, Australia, India, dll.).';
COMMENT ON COLUMN raw_geopolitik.raw_un_comtrade.volume_ribu_ton IS 'Volume fisik barang dalam ribuan ton (Ribu Ton).';
COMMENT ON COLUMN raw_geopolitik.raw_un_comtrade.nilai_fob_cif_juta_usd IS 'Nilai perdagangan dalam valuta USD (Juta USD).';
COMMENT ON COLUMN raw_geopolitik.raw_un_comtrade.pertumbuhan_tahunan_pct IS 'Pertumbuhan nilai dibanding periode sama tahun sebelumnya (%).';
COMMENT ON COLUMN raw_geopolitik.raw_un_comtrade.data_source IS 'Lembaga penerbit resmi data statistik perdagangan.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_un_status_traktat_multilateral (Sumber: un/status_traktat_multilateral)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_un_status_traktat_multilateral (
    id_traktat TEXT,
    nama_konvensi_internasional TEXT,
    organisasi_penyimpan_depository TEXT,
    tanggal_adopsi_dunia TEXT,
    status_keikutsertaan_indonesia TEXT,
    dokumen_pengesahan_uu_ri TEXT,
    tanggal_penyerahan_instrumen TEXT,
    catatan_reservasi_deklarasi TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_un_status_traktat_multilateral IS 'un status_traktat_multilateral';
COMMENT ON COLUMN raw_geopolitik.raw_un_status_traktat_multilateral.id_traktat IS 'Nomor registrasi traktat multilateral UN Treaty Collection (misal: ''UNTC-XXVII-7'').';
COMMENT ON COLUMN raw_geopolitik.raw_un_status_traktat_multilateral.nama_konvensi_internasional IS 'Nama konvensi atau protokol internasional.';
COMMENT ON COLUMN raw_geopolitik.raw_un_status_traktat_multilateral.organisasi_penyimpan_depository IS 'Lembaga penyimpan traktat (Sekjen PBB, WIPO, IAEA, dll.).';
COMMENT ON COLUMN raw_geopolitik.raw_un_status_traktat_multilateral.tanggal_adopsi_dunia IS 'Waktu traktat diadopsi secara global (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_geopolitik.raw_un_status_traktat_multilateral.status_keikutsertaan_indonesia IS 'Status keikutsertaan (Pihak / Diratifikasi, Penandatangan, Belum Menjadi Pihak).';
COMMENT ON COLUMN raw_geopolitik.raw_un_status_traktat_multilateral.dokumen_pengesahan_uu_ri IS 'Nomor UU atau regulasi ratifikasi Indonesia (misal: ''UU No. 16 Tahun 2016'').';
COMMENT ON COLUMN raw_geopolitik.raw_un_status_traktat_multilateral.tanggal_penyerahan_instrumen IS 'Waktu deposit instrumen ratifikasi ke Sekjen PBB (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_geopolitik.raw_un_status_traktat_multilateral.catatan_reservasi_deklarasi IS 'Pernyataan deklarasi interpretatif atau reservasi pasal tertentu oleh RI.';
COMMENT ON COLUMN raw_geopolitik.raw_un_status_traktat_multilateral.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_un_voting_sidang_pbb (Sumber: un/voting_sidang_pbb)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_un_voting_sidang_pbb (
    nomor_resolusi TEXT,
    badan_pbb TEXT,
    tanggal_voting TEXT,
    judul_resolusi TEXT,
    posisi_indonesia TEXT,
    total_suara_in_favor BIGINT,
    total_suara_against BIGINT,
    total_abstain BIGINT,
    posisi_negara_mitra_utama TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_un_voting_sidang_pbb IS 'un voting_sidang_pbb';
COMMENT ON COLUMN raw_geopolitik.raw_un_voting_sidang_pbb.nomor_resolusi IS 'Nomor dokumen resolusi PBB (misal: ''A/RES/79/112'').';
COMMENT ON COLUMN raw_geopolitik.raw_un_voting_sidang_pbb.badan_pbb IS 'Badan pelaksana pemungutan suara (UN General Assembly / UN Security Council).';
COMMENT ON COLUMN raw_geopolitik.raw_un_voting_sidang_pbb.tanggal_voting IS 'Waktu pemungutan suara berlangsung (format YYYY-MM-DD).';
COMMENT ON COLUMN raw_geopolitik.raw_un_voting_sidang_pbb.judul_resolusi IS 'Substansi isu yang diputuskan dalam resolusi PBB.';
COMMENT ON COLUMN raw_geopolitik.raw_un_voting_sidang_pbb.posisi_indonesia IS 'Sikap suara RI (In Favor / Setuju, Against / Menolak, Abstain).';
COMMENT ON COLUMN raw_geopolitik.raw_un_voting_sidang_pbb.total_suara_in_favor IS 'Jumlah total negara anggota yang mendukung resolusi.';
COMMENT ON COLUMN raw_geopolitik.raw_un_voting_sidang_pbb.total_suara_against IS 'Jumlah total negara anggota yang menolak resolusi.';
COMMENT ON COLUMN raw_geopolitik.raw_un_voting_sidang_pbb.total_abstain IS 'Jumlah total negara anggota yang menyatakan abstain.';
COMMENT ON COLUMN raw_geopolitik.raw_un_voting_sidang_pbb.posisi_negara_mitra_utama IS 'Perbandingan sikap suara negara mitra strategis (ASEAN, AS, Tiongkok, dll.).';
COMMENT ON COLUMN raw_geopolitik.raw_un_voting_sidang_pbb.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_undp_hdi (Sumber: undp/hdi)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_undp_hdi (
    tahun BIGINT,
    negara TEXT,
    iso3 TEXT,
    skor_hdi DOUBLE PRECISION,
    peringkat_hdi_dunia BIGINT,
    angka_harapan_hidup_tahun DOUBLE PRECISION,
    harapan_lama_sekolah_tahun DOUBLE PRECISION,
    rata_rata_lama_sekolah_tahun DOUBLE PRECISION,
    gni_per_kapita_ppp_usd DOUBLE PRECISION,
    kategori_hdi TEXT,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_undp_hdi IS 'undp hdi';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.tahun IS 'Tahun laporan atau observasi Human Development Index.';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.negara IS 'Nama negara (misal: Indonesia, Malaysia, Singapore).';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.iso3 IS 'Kode 3 huruf ISO3 negara (misal: IDN, MYS, SGP, USA).';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.skor_hdi IS 'Skor komposit Human Development Index (skala 0.000 - 1.000).';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.peringkat_hdi_dunia IS 'Peringkat pembangunan manusia global terkini.';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.angka_harapan_hidup_tahun IS 'Angka Harapan Hidup saat lahir dalam satuan tahun (Life Expectancy).';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.harapan_lama_sekolah_tahun IS 'Perkiraan lama sekolah yang diharapkan ditempuh anak usia sekolah (Expected Years of Schooling).';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.rata_rata_lama_sekolah_tahun IS 'Rata-rata lama sekolah riil yang dicapai penduduk usia 25 tahun ke atas (Mean Years of Schooling).';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.gni_per_kapita_ppp_usd IS 'Pendapatan Nasional Bruto per kapita berbasis Purchasing Power Parity dalam satuan USD (GNI per capita PPP).';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.kategori_hdi IS 'Klasifikasi tingkat pembangunan manusia: Very High (>=0.800), High (0.700-0.799), Medium (0.550-0.699), Low (<0.550).';
COMMENT ON COLUMN raw_geopolitik.raw_undp_hdi.data_source IS 'Sumber data resmi internasional.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_wipo_global_innovation_index (Sumber: wipo/global_innovation_index)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_wipo_global_innovation_index (
    tahun BIGINT,
    skor_gii_indonesia DOUBLE PRECISION,
    peringkat_gii_indonesia BIGINT,
    peringkat_asean BIGINT,
    pilar_institusi DOUBLE PRECISION,
    pilar_human_capital DOUBLE PRECISION,
    pilar_infrastruktur DOUBLE PRECISION,
    pilar_market_sophistication DOUBLE PRECISION,
    pilar_business_sophistication DOUBLE PRECISION,
    pilar_knowledge_technology DOUBLE PRECISION,
    pilar_creative_outputs DOUBLE PRECISION,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_wipo_global_innovation_index IS 'wipo global_innovation_index';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.tahun IS 'Tahun pemeringkatan indeks inovasi global (misal: 2026).';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.skor_gii_indonesia IS 'Skor komposit Global Innovation Index Indonesia (skala 0-100).';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.peringkat_gii_indonesia IS 'Peringkat inovasi Indonesia di antara 133 ekonomi dunia.';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.peringkat_asean IS 'Peringkat inovasi di kawasan ASEAN.';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.pilar_institusi IS 'Skor pilar kelembagaan institusi (Institutions).';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.pilar_human_capital IS 'Skor pilar modal manusia dan riset (Human Capital & Research).';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.pilar_infrastruktur IS 'Skor pilar infrastruktur teknologi & inovasi (Infrastructure).';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.pilar_market_sophistication IS 'Skor pilar kecanggihan pasar modal & kredit (Market Sophistication).';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.pilar_business_sophistication IS 'Skor pilar kecanggihan bisnis & pekerja berbasis pengetahuan (Business Sophistication).';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.pilar_knowledge_technology IS 'Skor pilar keluaran pengetahuan & teknologi (Knowledge & Technology Outputs).';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.pilar_creative_outputs IS 'Skor pilar luaran kreatif & hak cipta industri (Creative Outputs).';
COMMENT ON COLUMN raw_geopolitik.raw_wipo_global_innovation_index.data_source IS 'Lembaga penerbit resmi data.';

-- --------------------------------------------------------
-- Tabel: raw_geopolitik.raw_world_bank_indikator_makro (Sumber: world_bank/indikator_makro)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_geopolitik.raw_world_bank_indikator_makro (
    negara TEXT,
    kode_iso3 TEXT,
    kawasan TEXT,
    tahun BIGINT,
    populasi_juta_jiwa DOUBLE PRECISION,
    pdb_nominal_miliar_usd DOUBLE PRECISION,
    pdb_per_kapita_usd DOUBLE PRECISION,
    pertumbuhan_pdb_pct DOUBLE PRECISION,
    inflasi_pct DOUBLE PRECISION,
    nilai_ekspor_ri_ke_mitra_usd DOUBLE PRECISION,
    nilai_impor_ri_dari_mitra_usd DOUBLE PRECISION,
    neraca_perdagangan_ri_usd DOUBLE PRECISION,
    data_source TEXT
);

COMMENT ON TABLE raw_geopolitik.raw_world_bank_indikator_makro IS 'world_bank indikator_makro';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.negara IS 'Nama negara mitra diplomatik atau negara pembanding (misal: ''Indonesia'', ''Jepang'', ''Tiongkok'').';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.kode_iso3 IS 'Kode resmi 3 huruf ISO3 negara (misal: ''IDN'', ''JPN'', ''CHN'', ''USA'').';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.kawasan IS 'Kawasan geopolitik (misal: ''Asia Tenggara'', ''Asia Timur'', ''Amerika Utara'', ''Eropa'').';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.tahun IS 'Tahun kalender observasi indikator makroekonomi.';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.populasi_juta_jiwa IS 'Jumlah penduduk total negara dalam satuan juta jiwa.';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.pdb_nominal_miliar_usd IS 'Produk Domestik Bruto (PDB) nominal negara dalam satuan miliar USD.';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.pdb_per_kapita_usd IS 'Produk Domestik Bruto per kapita dalam satuan USD.';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.pertumbuhan_pdb_pct IS 'Laju pertumbuhan ekonomi / PDB riil tahunan dalam persen (%).';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.inflasi_pct IS 'Tingkat inflasi tahunan (Consumer Price Index) dalam persen (%).';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.nilai_ekspor_ri_ke_mitra_usd IS 'Total nilai ekspor barang/jasa dari Indonesia ke negara mitra dalam USD.';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.nilai_impor_ri_dari_mitra_usd IS 'Total nilai impor barang/jasa Indonesia dari negara mitra dalam USD.';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.neraca_perdagangan_ri_usd IS 'Surplus atau defisit neraca perdagangan bilateral Indonesia dalam USD.';
COMMENT ON COLUMN raw_geopolitik.raw_world_bank_indikator_makro.data_source IS 'Lembaga penerbit resmi data internasional.';
