"""Offline tests for Setneg official positions (Posisi Resmi Indonesia)."""

from datetime import date

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.setpres.posisi_resmi_indonesia.extractor import (
    Extractor,
    build_rows,
    classify,
    infer_official,
    parse_article,
    parse_id_date,
)
from ingestion.usecases.geopolitik.setpres.posisi_resmi_indonesia.models import Record

URL = "https://www.setneg.go.id/baca/index/pernyataan_pers_bersama_contoh"

HTML = """<html><body>
<h1 id="title-page">Pernyataan Pers Bersama Presiden RI usai Pertemuan Bilateral dengan Presiden Contoh</h1>
<div class="article-content">
<p class="widget-metas">Rabu, 28 Mei 2025 Di baca 10 kali</p>
<p>Di Istana Merdeka, Jakarta</p>
<p>Kami sepakat mendorong hubungan dagang dan investasi yang lebih seimbang.</p>
<p>Indonesia terus mendukung kemerdekaan Palestina melalui solusi two-states.</p>
<p>Presiden Prabowo menegaskan pentingnya dialog.</p>
<p>Bagaimana pendapat Anda?</p>
<div class="col-related"><p>Berita terkait perdagangan</p></div>
</div></body></html>"""


def test_parse_id_date():
    assert parse_id_date("Rabu, 28 Mei 2025 Di baca") == date(2025, 5, 28)
    assert parse_id_date("tanpa tanggal") is None


def test_classify_picks_earliest_keyword_group():
    assert classify("Indonesia mendukung Palestina dan perdagangan") == "Palestina dan Timur Tengah"
    assert classify("Perdagangan bebas dan kerja sama") == "Perdagangan dan investasi"
    assert classify("Salam hangat") is None


def test_parse_article_and_build_rows():
    article = parse_article(HTML)
    assert article["date"] == date(2025, 5, 28)
    assert "Berita terkait perdagangan" not in article["paragraphs"]
    assert not any(p.startswith("Bagaimana") for p in article["paragraphs"])

    rows = build_rows(article, URL)
    assert [r["isu"] for r in rows] == ["Perdagangan dan investasi", "Palestina dan Timur Tengah"]
    assert rows[0]["pejabat"] == "Presiden RI Prabowo Subianto"
    assert "Istana Merdeka" in rows[0]["forum_konteks"]
    assert rows[0]["tanggal_pernyataan"] == "2025-05-28"
    record = Record(**rows[1])
    assert record.url_sumber == URL and record.tanggal_pernyataan == date(2025, 5, 28)
    assert [r["urutan_isu"] for r in rows] == [1, 2]
    assert record.urutan_isu == 2


def test_repeated_issue_blocks_get_distinct_sequence_numbers():
    article = {
        "title": "Pernyataan Pers Bersama",
        "date": date(2025, 5, 28),
        "paragraphs": [
            "Kita sepakat mendorong perdagangan dan investasi.",
            "Presiden juga menyinggung Palestina dan Gaza.",
            "Kerja sama perdagangan dan investasi akan ditingkatkan.",
        ],
    }
    rows = build_rows(article, URL)
    keys = [(r["url_sumber"], r["urutan_isu"]) for r in rows]
    assert len(keys) == len(set(keys))


def test_infer_official():
    assert infer_official("Keterangan Pers Menteri Luar Negeri", "") == "Menteri Luar Negeri RI"
    assert infer_official("Pernyataan Presiden", "Presiden Prabowo berkata") == "Presiden RI Prabowo Subianto"
    assert infer_official("Judul netral", "") is None


def test_unknown_layout_and_empty_result_raise():
    with pytest.raises(SourceUnavailable):
        parse_article("<html><body><p>x</p></body></html>")

    class StubHttp:
        def get(self, url, **kwargs):
            class Resp:
                text = "<html><body><h1 id='title-page'>Judul</h1><div class='article-content'><p>Salam.</p></div></body></html>"

            return Resp()

    extractor = Extractor({"usecase": "geopolitik", "url": URL})
    extractor.http = StubHttp()
    with pytest.raises(SourceUnavailable):
        list(extractor.extract())


def _list_html(*slugs):
    return "<html><body>" + "".join(f'<a href="/baca/index/{s}">x</a>' for s in ("protokol", *slugs, "protokol")) + "</body></html>"


def test_discover_urls_follows_all_list_pages_until_empty():
    pages = {
        "https://l/x": _list_html("pernyataan_pers_bersama_a", "berita_biasa"),
        "https://l/x/10": _list_html("keterangan_pers_kunjungan_b"),
        "https://l/x/20": _list_html("pernyataan_pers_bersama_c"),
        "https://l/x/30": _list_html(),
    }

    class Http:
        def __init__(self):
            self.urls = []

        def get(self, url, **kwargs):
            self.urls.append(url)

            class Resp:
                text = pages[url]

            return Resp()

    extractor = Extractor({"usecase": "geopolitik"})
    extractor.http = Http()
    found = extractor.discover_urls("https://l/x")
    assert [u.rsplit("/", 1)[1] for u in found] == [
        "pernyataan_pers_bersama_a", "keterangan_pers_kunjungan_b", "pernyataan_pers_bersama_c",
    ]
    assert len(extractor.http.urls) == 4


def test_long_position_is_kept_in_full():
    long_text = "Kerja sama dagang dan investasi diperkuat. " * 80
    article = {"title": "Pernyataan Pers Presiden", "date": None, "paragraphs": [long_text.strip()]}
    rows = build_rows(article, URL)
    assert rows[0]["posisi_yang_dinyatakan"] == long_text.strip()
