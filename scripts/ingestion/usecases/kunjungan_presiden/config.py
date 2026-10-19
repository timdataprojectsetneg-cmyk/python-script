"""Usecase: Kunjungan Presiden — use case configuration."""

USECASE = "kunjungan_presiden"
DISPLAY_NAME = "Kunjungan Presiden"

SOURCES = {
    "prakiraan_cuaca": {"access": "api", "frequency": "realtime"},
    "hubud_bandara": {"access": "api", "frequency": "daily"},
    "siranap_rs_rujukan": {"access": "scraper", "frequency": "daily"},
    "matriks_risiko_kunjungan": {"access": "scraper", "frequency": "event_driven"},
    "matriks_janji_presiden": {"access": "scraper", "frequency": "monthly"},
    "statistik_kunjungan_presiden": {"access": "scraper", "frequency": "event_driven"},
    "tracking_arahan_lapangan": {"access": "scraper", "frequency": "monthly"},
    "susunan_pemerintahan_daerah": {"access": "scraper", "frequency": "monthly"},
    "idm": {"access": "api", "frequency": "yearly"},
    "rekap_aduan_wilayah": {"access": "api", "frequency": "daily"},
    "profil_sosioekonomi": {"access": "api", "frequency": "yearly"},
    "simkopdes_kdmp": {"access": "scraper", "frequency": "monthly"},
    "sppg_mbg": {"access": "api", "frequency": "daily"},
    "kampung_nelayan_merah_putih": {"access": "scraper", "frequency": "monthly"},
    "satusehat_ckg": {"access": "api", "frequency": "daily"},
    "sentimen_wilayah": {"access": "api", "frequency": "realtime"},
}
