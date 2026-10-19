"""Usecase: Geopolitik — use case configuration."""

USECASE = "geopolitik"
DISPLAY_NAME = "Geopolitik"

SOURCES = {
    "chokepoints_maritim": {"access": "api", "frequency": "daily"},
    "harga_minyak_mentah_icp": {"access": "scraper", "frequency": "monthly"},
    "sanksi_perdagangan": {"access": "api", "frequency": "weekly"},
    "comtrade": {"access": "api", "frequency": "monthly"},
    "safe_travel": {"access": "api", "frequency": "daily"},
    "sebaran_wni_pmi": {"access": "scraper", "frequency": "yearly"},
    "kasus_wni": {"access": "scraper", "frequency": "monthly"},
    "notam": {"access": "scraper", "frequency": "daily"},
    "kedaruratan_bencana": {"access": "api", "frequency": "hourly"},
    "amti_insiden_maritim": {"access": "scraper", "frequency": "weekly"},
    "konflik_global": {"access": "csv", "frequency": "monthly"},
    "ews_geopolitik": {"access": "api", "frequency": "daily"},
    "belanja_militer": {"access": "excel", "frequency": "yearly"},
    "indikator_makro": {"access": "api", "frequency": "yearly"},
    "treaty_room": {"access": "scraper", "frequency": "monthly"},
    "pertemuan_bilateral": {"access": "scraper", "frequency": "event_driven"},
    "iuran_organisasi_internasional": {"access": "scraper", "frequency": "yearly"},
    "voting_sidang_pbb": {"access": "scraper", "frequency": "event_driven"},
    "status_traktat_multilateral": {"access": "scraper", "frequency": "monthly"},
    "hdi": {"access": "csv", "frequency": "yearly"},
    "global_innovation_index": {"access": "scraper", "frequency": "yearly"},
    "media_asing": {"access": "api", "frequency": "realtime"},
    "klarifikasi_hoaks": {"access": "scraper", "frequency": "daily"},
}
