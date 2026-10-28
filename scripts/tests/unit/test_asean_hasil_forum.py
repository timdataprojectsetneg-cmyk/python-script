"""Offline tests for ASEAN Chairman's Statement (Hasil Forum)."""

from datetime import date

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.asean.hasil_forum import extractor as ext
from ingestion.usecases.geopolitik.asean.hasil_forum.extractor import (
    Extractor,
    parse_header,
    parse_statement,
    smart_title,
)
from ingestion.usecases.geopolitik.asean.hasil_forum.models import Record

TEXT = """FINAL
1

CHAIRMAN’S STATEMENT OF THE 46TH ASEAN SUMMIT
KUALA LUMPUR, MALAYSIA, 26 MAY 2025

1. We, the Member States  of ASEAN, gathered in Kuala Lumpur on 26 May 2025 for the
46th ASEAN Summit.

2. We reaffirmed our support for Malaysia’s ASEAN Chairmanship.

ASEAN COMMUNITY-BUILDING

3. We recognised the progress across the Political-Security, Economic, and Socio -
Cultural pillars, including intra -ASEAN trade.
2

4. We welcomed the plan , which will serve as a roadmap.

KEY DELIVERABLES

Theme: "Inclusivity and Sustainability"

5. We reaffirmed our commitment to ASEAN
Centrality.

ASEAN SECTORAL DIALOGUE PARTNERS AND ASEAN DEVELOPMENT
PARTNERS

6. We welcomed the Dialogue Partners.
"""


def test_smart_title_keeps_acronyms_ordinals_and_hyphen_parts():
    assert smart_title("CHAIRMAN’S STATEMENT OF THE 46TH ASEAN SUMMIT") == "Chairman’s Statement of the 46th ASEAN Summit"
    assert smart_title("ASEAN COMMUNITY-BUILDING") == "ASEAN Community-Building"
    assert smart_title("ASEAN PLUS THREE (APT)") == "ASEAN Plus Three (APT)"


def test_parse_header_reads_title_and_date():
    title, when = parse_header(TEXT.splitlines())
    assert title == "Chairman’s Statement of the 46th ASEAN Summit"
    assert when == date(2025, 5, 26)


def test_parse_statement_numbers_paragraphs_and_assigns_headings():
    rows = parse_statement(TEXT)
    assert [r["paragraf"] for r in rows] == [1, 2, 3, 4, 5, 6]
    assert [r["isu"] for r in rows] == [
        None,
        None,
        "ASEAN Community-Building",
        "ASEAN Community-Building",
        "Key Deliverables",
        "ASEAN Sectoral Dialogue Partners and ASEAN Development Partners",
    ]
    assert all(r["tanggal_forum"] == date(2025, 5, 26) for r in rows)
    assert all(r["forum"] == "Chairman’s Statement of the 46th ASEAN Summit" for r in rows)


def test_parse_statement_cleans_wrapped_text_and_page_numbers():
    rows = parse_statement(TEXT)
    assert rows[0]["hasil_sikap_bersama"].startswith("We, the Member States of ASEAN, gathered")
    assert rows[2]["hasil_sikap_bersama"].endswith("Socio-Cultural pillars, including intra-ASEAN trade.")
    assert rows[3]["hasil_sikap_bersama"] == "We welcomed the plan, which will serve as a roadmap."
    assert "Theme" not in rows[4]["hasil_sikap_bersama"]


def test_record_validates_row():
    record = Record(**parse_statement(TEXT)[2])
    assert record.paragraf == 3 and record.tanggal_forum == date(2025, 5, 26)


def test_extractor_raises_when_no_paragraphs(monkeypatch):
    monkeypatch.setattr(Extractor, "_load_pdf", lambda self: b"%PDF")
    monkeypatch.setattr(ext, "pdf_text", lambda content: "nothing numbered")
    with pytest.raises(SourceUnavailable):
        list(Extractor({}).extract())
