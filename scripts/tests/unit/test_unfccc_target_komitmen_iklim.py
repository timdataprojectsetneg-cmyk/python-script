"""Offline tests for UNFCCC Second NDC climate targets (Target Komitmen Iklim)."""

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.unfccc.target_komitmen_iklim import extractor as ext
from ingestion.usecases.geopolitik.unfccc.target_komitmen_iklim.extractor import (
    Extractor,
    extract_facts,
    normalize,
    parse_number,
)
from ingestion.usecases.geopolitik.unfccc.target_komitmen_iklim.models import Record

PAGES = [
    "Cover page without numbers",
    """Under the LCCP scenarios, Indonesia is expected to achieve its peak
emissions by 2030, with estimated emission levels of 1,345,707 Gg CO 2e
under the LCCP_L scenario and 1,491,474 Gg CO 2e under the LCCP _H
scenario. Compared to the ENDC CM2 scenario, which projects emissions
of 1,632,000 Gg CO2e in 2030, Indonesia's emissions are expected to be 8 -
17.5% lower. The emissions will decline in 2035 with the projection of GHG
emission levels reaching 1,257,717 Gg CO2e under LCCP_L and 1,488,866
Gg CO2e under LCCP_H.""",
    """Level of Emission
2019 2
: 1,145,037 Gg CO 2e (GHGs inventory-based net emission).
CPOS and LCCP_L scenarios apply economic growth of 6. 0% in 2030
and 6.7% in 2035.""",
    """In 2030, level of emission under CPOS will be 55,5% above the reference emission, under LCCP_L, and
LCCP_H emission level will be 17.5% and 30.3% above the reference year respectively. In
2035, the level of emission under CPOS will be 56.1% above the reference year and under LCCP_L, and
LCCP_H will be 9.8% and 30.0% above the reference year respectively.""",
    "Level of Emission 2019: 1,145,037 Gg CO2e repeated on a later page.",
]


def find(rows, indikator, skenario, tahun):
    return next(r for r in rows if r["indikator"] == indikator and r["skenario_konteks"] == skenario and r["tahun_target"] == tahun)


def test_parse_number_handles_thousands_and_decimal_comma():
    assert parse_number("1,345,707") == 1345707.0
    assert parse_number("55,5") == 55.5
    assert parse_number("17.5") == 17.5
    assert parse_number("472.6.") == 472.6


def test_normalize_repairs_pypdf_spacing():
    assert normalize("1,345,707  Gg CO 2e under LCCP _H at 6. 0 %") == "1,345,707 Gg CO2e under LCCP_H at 6.0%"


def test_extract_facts_reads_absolute_projections_with_pages():
    rows = extract_facts(PAGES)
    peak = find(rows, "Proyeksi emisi GHG nasional (puncak emisi)", "LCCP_L", 2030)
    assert (peak["nilai_bawah"], peak["nilai_atas"], peak["satuan"], peak["halaman_pdf"]) == (1345707.0, 1345707.0, "Gg CO2e", 2)
    assert find(rows, "Proyeksi emisi GHG nasional", "LCCP_H", 2035)["nilai_atas"] == 1488866.0
    assert find(rows, "Proyeksi emisi GHG nasional", "ENDC CM2", 2030)["nilai_bawah"] == 1632000.0


def test_extract_facts_keeps_ranges_as_lower_and_upper():
    row = find(extract_facts(PAGES), "Emisi LCCP lebih rendah dibanding ENDC CM2", "LCCP_L dan LCCP_H vs ENDC CM2", 2030)
    assert (row["nilai_bawah"], row["nilai_atas"], row["satuan"]) == (8.0, 17.5, "%")


def test_extract_facts_reads_percent_above_reference_and_growth():
    rows = extract_facts(PAGES)
    above = "Level emisi relatif terhadap emisi tahun referensi 2019"
    assert find(rows, above, "CPOS", 2030)["nilai_bawah"] == 55.5
    assert find(rows, above, "LCCP_H", 2035)["nilai_bawah"] == 30.0
    assert find(rows, "Asumsi pertumbuhan ekonomi", "CPOS dan LCCP_L", 2030)["nilai_bawah"] == 6.0


def test_extract_facts_deduplicates_repeated_facts_keeping_first_page():
    reference = [r for r in extract_facts(PAGES) if r["indikator"].startswith("Emisi GHG bersih tahun referensi")]
    assert len(reference) == 1 and reference[0]["halaman_pdf"] == 3


def test_record_validates_row():
    record = Record(**extract_facts(PAGES)[0])
    assert record.halaman_pdf == 2 and record.nilai_bawah is not None


def test_extractor_defaults_to_chrome_impersonation():
    assert Extractor({}).impersonate == "chrome"
    assert Extractor({"impersonate": "safari"}).impersonate == "safari"


def test_extractor_raises_when_no_indicator_matches(monkeypatch):
    monkeypatch.setattr(Extractor, "_load_pdf", lambda self: b"%PDF")
    monkeypatch.setattr(ext, "pdf_pages", lambda content: ["nothing relevant"])
    with pytest.raises(SourceUnavailable):
        list(Extractor({}).extract())
