"""Unit tests for Kemlu RI Safe Travel Appeals Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.kemlu.safe_travel.models import Record, SafeTravelRecord
from ingestion.usecases.geopolitik.kemlu.safe_travel.normalizer import (
    Normalizer,
    parse_date,
    clean_text,
    resolve_country_and_region,
    resolve_alert_level,
    resolve_trigger,
)
from ingestion.usecases.geopolitik.kemlu.safe_travel.extractor import Extractor


def test_models_validation_valid():
    """Verify that a properly populated record passes Pydantic validation."""
    data = {
        "negara": "Iran",
        "kawasan": "Timur Tengah",
        "level_peringatan": "Level 3 - Hati-hati (Oranye)",
        "ringkasan_imbauan": "WNI diimbau menunda perjalanan non-esensial dan segera lapor diri.",
        "tanggal_rilis": "2026-10-02",
        "pemicu_peringatan": "Konflik Bersenjata & Kerawanan Keamanan",
        "nomor_hotline_kbri_kjri": "+98 912 123 4567",
        "news_id": "appeal-12345",
        "uuid": "appeal-12345",
        "news_title": "Imbauan Keamanan WNI di Iran",
        "news_info": "Keamanan",
        "news_image_path": "https://safetravel.kemlu.go.id/img/iran.jpg",
        "news_total_read": 1500,
        "data_source": "Kementerian Luar Negeri RI - Portal Safe Travel"
    }
    rec = Record(**data)
    assert rec.negara == "Iran"
    assert rec.kawasan == "Timur Tengah"
    assert rec.tanggal_rilis == "2026-10-02"
    assert rec.level_peringatan == "Level 3 - Hati-hati (Oranye)"


def test_models_validation_defaults():
    """Verify model default values for minimal payload."""
    rec = Record(
        ringkasan_imbauan="Imbauan umum perjalanan internasional.",
        tanggal_rilis="2026-10-14"
    )
    assert rec.negara == "Global / Semua Negara"
    assert rec.kawasan == "Global"
    assert rec.level_peringatan == "Level 1 - Aman (Hijau)"
    assert rec.pemicu_peringatan == "Informasi Umum & Regulasi"
    assert rec.data_source == "Kementerian Luar Negeri RI - Portal Safe Travel"


def test_date_parser_indonesian():
    """Verify Indonesian natural date format conversion to ISO YYYY-MM-DD."""
    assert parse_date("1 Agustus 2026") == "2026-08-01"
    assert parse_date("26 Agustus 2026") == "2026-08-26"
    assert parse_date("17 Mei 2026") == "2026-05-17"
    assert parse_date("31 Desember 2025") == "2025-12-31"
    assert parse_date("") == ""


def test_clean_text():
    """Verify HTML and special character stripping."""
    raw = "   \xa0<p>Pemerintah Viet Nam <b>memberlakukan</b> bebas visa.</p>\r\n   "
    cleaned = clean_text(raw)
    assert "<b>" not in cleaned
    assert "<p>" not in cleaned
    assert "\xa0" not in cleaned
    assert "Pemerintah Viet Nam memberlakukan bebas visa." in cleaned


def test_resolve_country_and_region():
    """Verify country and region detection."""
    # From country names
    c, r = resolve_country_and_region("", ["Nepal"], "Bencana Banjir", "Sungai meluap")
    assert c == "Nepal"
    assert r == "Asia Selatan"

    # From title when country is 'Semua Negara'
    c2, r2 = resolve_country_and_region("Semua Negara", ["Semua Negara"], "Gempa Bumi di Kolombia", "Pusat gempa di Choco")
    assert c2 == "Kolombia"
    assert r2 == "Amerika Latin"

    # Global fallback
    c3, r3 = resolve_country_and_region("Semua Negara", ["Semua Negara"], "Imbauan Perjalanan Libur Akhir Tahun", "Waspada penipuan")
    assert c3 == "Global / Semua Negara"
    assert r3 == "Global"


def test_resolve_alert_level():
    """Verify alert level classifications."""
    assert resolve_alert_level("Evakuasi WNI", "WNI diminta hindari perjalanan", "Keamanan") == "Level 4 - Bahaya / Hindari (Merah)"
    assert resolve_alert_level("Gempa Bumi 7.4", "Hati-hati terhadap gempa susulan", "Keamanan") == "Level 3 - Hati-hati (Oranye)"
    assert resolve_alert_level("Waspada Cuaca Ekstrem", "Imbauan tetap waspada di kerumunan", "Umum") == "Level 2 - Waspada (Kuning)"
    assert resolve_alert_level("Bebas Visa", "Kunjungan singkat 14 hari", "Keimigrasian") == "Level 1 - Aman (Hijau)"


def test_resolve_trigger():
    """Verify trigger categorizations."""
    assert resolve_trigger("Banjir Bandang", "Daerah aliran sungai", "Keamanan") == "Bencana Alam"
    assert resolve_trigger("Wabah Ebola", "WHO menetapkan PHEIC", "Kesehatan") == "Wabah Penyakit / Krisis Kesehatan"
    assert resolve_trigger("Konflik Bersenjata", "Baku tembak militer", "Keamanan") == "Konflik Bersenjata & Kerawanan Keamanan"
    assert resolve_trigger("Bebas Visa", "Paspor biasa kunjungan", "Keimigrasian") == "Kebijakan Keimigrasian & Perjalanan"


def test_normalizer_flow():
    """Verify end-to-end normalization from raw API payload."""
    raw_records = [
        {
            "news_id": "test-uuid-001",
            "uuid": "test-uuid-001",
            "news_title": "Kebijakan Bebas Visa bagi WNI di Viet Nam",
            "news_content": "Pemerintah Viet Nam memberlakukan bebas visa 14 hari. Kontak KBRI Hanoi: +84 24 3825 3353",
            "news_date": "1 Agustus 2026",
            "news_total_read": 100,
            "news_info": "Keimigrasian",
            "news_image_path": "https://safetravel.kemlu.go.id/img.jpg",
            "news_country_names": ["Viet Nam"],
            "news_country_name": "Viet Nam"
        }
    ]
    norm = Normalizer()
    results = list(norm.normalize(iter(raw_records)))
    assert len(results) == 1
    item = results[0]
    assert item["negara"] == "Viet Nam"
    assert item["kawasan"] == "Asia Tenggara"
    assert item["tanggal_rilis"] == "2026-08-01"
    assert item["level_peringatan"] == "Level 1 - Aman (Hijau)"
    assert "+84 24 3825 3353" in item["nomor_hotline_kbri_kjri"]


def test_extractor_records_from():
    """Verify extractor parsing logic for both list and dict payload."""
    ext = Extractor({"url": "https://safetravel.kemlu.go.id/api/appeal"})
    list_payload = [{"news_id": "1"}, {"news_id": "2"}]
    assert len(ext._records_from(list_payload)) == 2

    dict_payload = {"data": [{"news_id": "1"}, {"news_id": "2"}, {"news_id": "3"}]}
    assert len(ext._records_from(dict_payload)) == 3
