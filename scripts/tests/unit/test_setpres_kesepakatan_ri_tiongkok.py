"""Offline tests for Setneg RI-Tiongkok agreements (Kesepakatan RI-Tiongkok)."""

from datetime import date

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.setpres.kesepakatan_ri_tiongkok.extractor import (
    Extractor,
    article_date,
    build_rows,
    extract_agreements,
    parse_article,
)
from ingestion.usecases.geopolitik.setpres.kesepakatan_ri_tiongkok.models import Record

URL = "https://www.setneg.go.id/baca/index/contoh_nota_kesepahaman"

HTML = """<html><body>
<h1 id="title-page">Presiden Saksikan Penandatanganan Nota Kesepahaman RI-Tiongkok</h1>
<div class="article-content">
<p class="widget-metas">Minggu, 25 Mei 2025 Di baca 5 kali</p>
<p>Presiden menyaksikan penandatanganan nota kesepahaman di Jakarta, Minggu (25/05/2025).</p>
<p>Salah satu nota kesepahaman utama adalah antara Kementerian Perdagangan RI dan Kementerian Perdagangan RRT mengenai Penguatan Rantai Pasok. Selain itu, Bank Indonesia dan People's Bank of China menyepakati pembentukan kerangka transaksi mata uang lokal.</p>
<p>Ditandatangani dua dokumen kerja sama antara Kementerian Kesehatan RI dan lembaga kesehatan RRT mengenai pengobatan tradisional dan penanggulangan tuberkulosis.</p>
<p>Protokol ekspor durian beku ditandatangani oleh otoritas karantina kedua negara.</p>
<p>Penandatanganan juga mencakup kerja sama investasi antara Danantara dan China Investment Corporation, serta penguatan hubungan antara Kamar Dagang dan Industri Indonesia (Kadin) dan Kamar Dagang Tiongkok di Indonesia.</p>
<p>Bagaimana pendapat Anda?</p>
</div></body></html>"""


def test_article_date_prefers_body_date():
    assert article_date("Senin, 26 Mei 2025", "ditandatangani (25/05/2025)") == date(2025, 5, 25)
    assert article_date("Senin, 26 Mei 2025", "tanpa tanggal") == date(2025, 5, 26)
    assert article_date("", "") is None


def test_extract_agreements_between_and_assign_sides():
    [item] = extract_agreements(
        "antara Kementerian Perdagangan RI dan Kementerian Perdagangan RRT mengenai Penguatan Rantai Pasok"
    )
    assert item["indonesia"] == "Kementerian Perdagangan RI"
    assert item["mitra"] == "Kementerian Perdagangan RRT"
    assert item["topic"] == "Penguatan Rantai Pasok"


def test_extract_agreements_counted_items_expand():
    items = extract_agreements(
        "dua dokumen kerja sama antara Kementerian Kesehatan RI dan lembaga kesehatan RRT "
        "mengenai pengobatan tradisional dan penanggulangan tuberkulosis"
    )
    assert [i["topic"] for i in items] == ["Pengobatan tradisional", "Penanggulangan tuberkulosis"]
    assert {i["mitra"] for i in items} == {"lembaga kesehatan RRT"}


def test_extract_agreements_both_authorities_and_none():
    [item] = extract_agreements("Protokol ekspor durian beku ditandatangani oleh otoritas karantina kedua negara")
    assert item["indonesia"] == "otoritas karantina Indonesia"
    assert item["mitra"] == "otoritas karantina Tiongkok"
    assert extract_agreements("Momentum ini menjadi bukti kemitraan strategis") == []


def test_build_rows_from_article_validates_record():
    article = parse_article(HTML)
    rows = build_rows(article, URL)
    topics = [r["topik_kesepakatan"] for r in rows]
    assert "Penguatan Rantai Pasok" in topics
    assert "Pengobatan tradisional" in topics and "Penanggulangan tuberkulosis" in topics
    assert any(t.startswith("Penguatan hubungan antara Kamar Dagang dan Industri Indonesia (Kadin)") for t in topics)
    kadin = next(r for r in rows if r["pihak_mitra"] == "Kamar Dagang Tiongkok di Indonesia")
    assert kadin["pihak_indonesia"] == "Kamar Dagang dan Industri Indonesia (Kadin)"
    for row in rows:
        record = Record(**row)
        assert record.tanggal == date(2025, 5, 25)
        assert record.status_bukti.startswith("Ditandatangani")
        assert record.url_sumber == URL
    numbers = [r["urutan_kesepakatan"] for r in rows]
    assert numbers == list(range(1, len(rows) + 1))


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
