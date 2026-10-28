"""Offline tests for Kemlu Imbauan dan Status Siaga (rule-based article extraction)."""

from datetime import date

import pytest

from ingestion.exceptions import ConfigError, SourceUnavailable
from ingestion.usecases.geopolitik.kemlu.imbauan_status_siaga import extractor as ext
from ingestion.usecases.geopolitik.kemlu.imbauan_status_siaga.extractor import Extractor, parse_article
from ingestion.usecases.geopolitik.kemlu.imbauan_status_siaga.models import Record

SIAGA_HTML = """
<html><head><meta property="article:published_time" content="2025-06-20T08:00:00+07:00"></head><body>
<h1>Kemlu Tingkatkan Status Siaga 1 bagi WNI di Iran</h1>
<p>Jakarta, 20 Juni 2025. Kementerian Luar Negeri meningkatkan status menjadi Siaga 1 di Iran.
KBRI Teheran mengimbau WNI untuk meninggalkan wilayah rawan. Sebanyak 386 WNI tercatat di Iran.</p>
<p>Proses evakuasi bertahap disiapkan oleh KBRI Teheran.</p></body></html>
"""
IMBAUAN_HTML = """
<h1>KBRI Muscat Mengimbau Waspada Penipuan di Oman</h1>
<p>Muscat, 27 Januari 2026. KBRI Muscat mengimbau WNI agar tidak mengirim uang kepada pihak yang mengaku staf KBRI.
Masyarakat diimbau melapor jika menemukan modus penipuan serupa dan sebaiknya berhati-hati.</p>
"""
IRRELEVANT_HTML = "<h1>Menlu Hadiri Pertemuan di Jakarta</h1><p>" + "Pertemuan bilateral membahas kerja sama ekonomi. " * 5 + "</p>"
NO_COUNTRY_HTML = "<h1>Imbauan umum perjalanan</h1><p>" + "Kemlu mengimbau WNI agar berhati-hati saat bepergian ke luar negeri. " * 3 + "</p>"
SPA_SHELL = '<html><head><title>Portal Kemlu</title></head><body><div id="app"></div></body></html>'


def test_siaga_article_gives_level_country_count_and_date():
    recs = parse_article(SIAGA_HTML, "https://kemlu.go.id/x")
    assert len(recs) == 1
    r = recs[0]
    assert r["status_jenis_imbauan"] == "Siaga I" and r["negara"] == "Iran"
    assert r["jumlah_wni_disebut_sumber"] == 386
    assert r["tanggal_acuan"] == date(2025, 6, 20)
    assert r["perwakilan_penerbit"] == "KBRI Teheran"
    assert r["url_bukti"] == "https://kemlu.go.id/x"
    assert "evakuasi" in r["tindakan_yang_diumumkan"].lower() or "meninggalkan" in r["tindakan_yang_diumumkan"].lower()
    assert Record(**r).negara == "Iran"


def test_imbauan_without_level_is_not_given_a_siaga_level():
    r = parse_article(IMBAUAN_HTML, "u")[0]
    assert r["status_jenis_imbauan"] == "Imbauan penipuan"
    assert r["negara"] == "Oman" and r["tanggal_acuan"] == date(2026, 1, 27)
    assert r["jumlah_wni_disebut_sumber"] is None


def test_irrelevant_or_countryless_or_shell_pages_are_skipped():
    assert parse_article(IRRELEVANT_HTML, "u") == []
    assert parse_article(NO_COUNTRY_HTML, "u") == []
    assert parse_article(SPA_SHELL, "u") == []


def test_ambiguous_wni_counts_stay_empty():
    assert ext.find_wni_count("Ada 10 WNI di sana dan 20 WNI di sini.") is None
    assert ext.find_wni_count("Tercatat 1.200 WNI di Suriah.") == 1200
    assert ext.find_wni_count("tidak ada angka") is None


def test_multiple_levels_give_one_record_each():
    html = "<h1>Status Siaga di Yaman</h1><p>Wilayah Hudaidah berstatus Siaga I. Wilayah selatan berstatus Siaga III di Yaman. " + "x " * 30 + "</p>"
    levels = sorted(r["status_jenis_imbauan"] for r in parse_article(html, "u"))
    assert levels == ["Siaga I", "Siaga III"]


def test_extractor_requires_input_and_fails_loudly(tmp_path):
    with pytest.raises(ConfigError):
        list(Extractor({}).extract())
    f = tmp_path / "shell.html"
    f.write_text(SPA_SHELL, encoding="utf-8")
    with pytest.raises(SourceUnavailable):
        list(Extractor({"source_file": str(f)}).extract())


def test_source_file_directory(tmp_path):
    (tmp_path / "a.html").write_text(SIAGA_HTML, encoding="utf-8")
    (tmp_path / "b.html").write_text(IMBAUAN_HTML, encoding="utf-8")
    rows = list(Extractor({"source_file": str(tmp_path)}).extract())
    assert sorted(r["negara"] for r in rows) == ["Iran", "Oman"]
