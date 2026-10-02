"""Listing-card parsing for the MA putusan (PHI) scraper."""

from bs4 import BeautifulSoup

from ingestion.usecases.ketenagakerjaan.mahkamah_agung_ri.direktori_putusan_perkara_pengadilan_hubungan.scraper.extractor import (  # noqa: E501
    build_row,
    detect_total_data,
    is_phi_case,
    page_url,
    parse_listing_item,
)

SPOST = """
<div class="spost clearfix"><div class="entry-c">
  <div class="small"><a href="https://putusan3.mahkamahagung.go.id/pengadilan/profil/pengadilan/pn-medan.html">PN MEDAN</a></div>
  <div class="small"><strong>Register :</strong> 07-01-2026 &#8212; <strong>Putus :</strong> 26-01-2026 &#8212; <strong>Upload :</strong> 26-01-2026</div>
  <strong><a href="https://putusan3.mahkamahagung.go.id/direktori/putusan/zaf0fa884aa73eaa8d63313432363132.html">Putusan PN MEDAN Nomor 10/Pdt.Sus-<mark>PHI</mark>/2026/PN Mdn</a></strong> <br>
  <div>Tanggal 26 Januari 2026 &#8212; Penggugat:<br />1.MUHAMMAD RUDIANDANI<br />2.NURIADI<br />3.HARIANTO<br />4.ROHAYATIN<br />Tergugat:<br />PT. USAHA PERKEBUNAN INDONESIA BAHRUNY (PT. BAHRUNY)<br />Turut Tergugat:<br />DINAS KETENAGAKERJAAN KABUPATEN LANGKAT<br> <i class="icon-eye icon-lg mr-1"></i><strong title="Jumlah view">22</strong> &#8212; <i class="icon-download icon-lg mr-1"></i><strong title="Jumlah download">9</strong></div>
  <ul class="nobottommargin"><li><blockquote><p><strong>MENETAPKAN</strong></p><ul><li>Menerima dan mengabulkan permohonan pencabutan gugatan Para Penggugat tersebut;</li><li>Menyatakan perkara gugatan dicabut;</li></ul></blockquote><blockquote>10/Pdt.Sus-<mark>PHI</mark>/2026/PN Mdn</blockquote></li></ul>
</div></div>
"""

SINGLE = """
<div class="spost clearfix"><div class="entry-c">
  <strong><a href="https://putusan3.mahkamahagung.go.id/direktori/putusan/z.html">Putusan PN BANDUNG Nomor 7/Pdt.Sus-<mark>PHI</mark>/2026/PN Bdg</a></strong> <br>
  <div>Tanggal 28 Januari 2026 &#8212; Penggugat:<br />Erwin Alvian<br />Tergugat:<br />PT.Dakota Logistik Indonesia<br> <i class="icon-eye"></i><strong title="Jumlah view">46</strong></div>
  <ul class="nobottommargin"><li><blockquote>MENETAPKAN: Mengabulkan Permohonan Pencabutan</blockquote></li></ul>
</div></div>
"""


VS_STYLE = """
<div class="spost clearfix"><div class="entry-c">
  <strong><a href="https://putusan3.mahkamahagung.go.id/direktori/putusan/11.html">Putusan MAHKAMAH AGUNG Nomor 10 K/PDT.SUS-<mark>PHI</mark>/2026</a></strong> <br>
  <div>Tanggal 3 Februari 2026 &#8212; AMUDIN HUTAPEA (Penggugat) VS PT.  Sumatera  Kartindo (Tergugat)<br> <i class="icon-eye icon-lg mr-1"></i><strong title="Jumlah view">33</strong> &#8212; <i class="icon-download icon-lg mr-1"></i><strong title="Jumlah download">14</strong></div>
  <ul class="nobottommargin"><li><blockquote>10 K/PDT.SUS-<mark>PHI</mark>/2026</blockquote></li></ul>
</div></div>
"""


def _item(html):
    return parse_listing_item(BeautifulSoup(html, "html.parser").select_one("div.spost"))


def test_listing_parties_multi_line_and_excludes_turut_tergugat():
    item = _item(SPOST)
    assert item["penggugat_listing"] == "MUHAMMAD RUDIANDANI; NURIADI; HARIANTO; ROHAYATIN"
    assert item["tergugat_listing"] == "PT. USAHA PERKEBUNAN INDONESIA BAHRUNY (PT. BAHRUNY)"


def test_listing_parties_single_line_stops_at_view_counter():
    item = _item(SINGLE)
    assert item["penggugat_listing"] == "Erwin Alvian"
    assert item["tergugat_listing"] == "PT.Dakota Logistik Indonesia"


def test_listing_summary_joins_blockquotes():
    summary = _item(SPOST)["ringkasan_listing"]
    assert "MENETAPKAN" in summary
    assert "Menyatakan perkara gugatan dicabut" in summary


def test_listing_parties_vs_style():
    item = _item(VS_STYLE)
    assert item["penggugat_listing"] == "AMUDIN HUTAPEA"
    assert item["tergugat_listing"] == "PT. Sumatera Kartindo"


def test_is_phi_case_filters_unrelated_hits():
    assert is_phi_case("Putusan PN MEDAN Nomor 10/Pdt.Sus-PHI/2026/PN Mdn")
    assert is_phi_case("10 K/PDT.SUS-PHI/2026")
    assert not is_phi_case("355/Pdt.P/2026/PA.PLG")
    assert not is_phi_case("7843 K/PID.SUS/2026")
    assert not is_phi_case("")


def test_detect_total_data():
    assert detect_total_data(BeautifulSoup("<div>Ditemukan 1780 data</div>", "html.parser")) == 1780
    assert detect_total_data(BeautifulSoup("<div>Ditemukan 1.780 data</div>", "html.parser")) == 1780
    assert detect_total_data(BeautifulSoup("<div>tidak ada</div>", "html.parser")) is None


def test_page_url_keeps_search_filters():
    base = "https://putusan3.mahkamahagung.go.id/search.html?q=PHI&obf=TANGGAL_PUTUS&obm=asc&t_reg=2026"
    assert page_url(base, 2) == base + "&page=2"
    assert page_url(base, 3) == base + "&page=3"
    assert page_url(base, 1) == base


def test_extract_uses_total_data_for_page_count_and_threads_pages():
    from ingestion.usecases.ketenagakerjaan.mahkamah_agung_ri.direktori_putusan_perkara_pengadilan_hubungan.scraper.extractor import (  # noqa: E501
        Extractor,
    )

    class FakeExtractor(Extractor):
        def _get_soup(self, http, url):
            return BeautifulSoup(
                '<div>Ditemukan 40 data</div>'
                '<div class="spost"><a href="/direktori/putusan/x.html">Putusan Nomor 1/Pdt.Sus-PHI/2026/PN X</a></div>',
                "html.parser",
            )

        def _page_rows(self, page, listing=None):
            return [{"nomor_perkara": f"{page}/Pdt.Sus-PHI/2026/PN X"}]

    rows = list(FakeExtractor({"url": "https://x/search.html?q=PHI"}).extract())
    assert sorted(row["nomor_perkara"] for row in rows) == [
        "1/Pdt.Sus-PHI/2026/PN X",
        "2/Pdt.Sus-PHI/2026/PN X",
    ]


def test_build_row_uses_listing_parties_and_summary():
    item = _item(SINGLE)
    row = build_row(item, {}, "")
    assert row["nama_penggugat"] == "Erwin Alvian"
    assert row["nama_perusahaan_tergugat"] == "PT.Dakota Logistik Indonesia"
    assert "Mengabulkan Permohonan Pencabutan" in row["ringkasan_pokok_sengketa"]
