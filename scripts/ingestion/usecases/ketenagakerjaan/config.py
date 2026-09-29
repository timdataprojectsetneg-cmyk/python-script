"""UC-01 Ketenagakerjaan — use case configuration."""

USECASE = "ketenagakerjaan"
DISPLAY_NAME = "Ketenagakerjaan"

SOURCES = {
    "kasus_perselisihan": {"access": "excel", "frequency": "monthly"},
    "data_mogok_kerja": {"access": "excel", "frequency": "monthly"},
    "upah_minimum_provinsi": {"access": "excel", "frequency": "yearly"},
    "bps_inflasi_yoy": {"access": "scraper", "frequency": "monthly"},
    "bps_inflasi_mom": {"access": "api", "frequency": "monthly"},
    "signal_ketenagakerjaan": {"access": "scraper", "frequency": "daily"},
}
