"""Offline tests for ASEAN Notional Calendar (Agenda Forum)."""

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.asean.agenda_forum import extractor as ext
from ingestion.usecases.geopolitik.asean.agenda_forum.extractor import (
    Extractor,
    find_calendar_links,
    parse_calendar_text,
    parse_entry,
    split_entries,
)
from ingestion.usecases.geopolitik.asean.agenda_forum.models import Record

TEXT = """ASEAN 2026 PUBLIC NOTIONAL CALENDAR as of 8 January 2026
No. of
Meetings Meeting/ Specific Activity Date  Venue Pillar
DECEMBER 2025
1 (CBIP Event) MSME Showcase and
Trade Fair Event 10-11 December 2025 (TBC) AEC
2 ASEAN Senior Economic Officials Meeting (SEOM) Retreat 2026 10-11 December 2025 Boracay,
Philippines
AEC
JANUARY
3
ASEAN Caucus for Special Meeting of the Rules of Origin
8 January 2026 Virtual AEC
4 Sub-Regional Meeting Q3 The Philippines APSC5 Consultation Meeting on Climate Change (TBC)
6 RCEP Leaders Summit Defer to DFA on the appropriate date Metro Manila, Philippines AEC
7 ACSI Meeting
8 January 2026 Metro Manila Cross-Pillar
"""


def test_split_entries_uses_sequential_numbers_and_glued_pillars():
    entries = split_entries(TEXT)
    assert [n for n, _ in entries] == [1, 2, 3, 4, 5, 6, 7]
    assert entries[0][1].startswith("(CBIP Event) MSME Showcase and Trade Fair Event")
    assert entries[2][1].startswith("ASEAN Caucus")


def test_parse_entry_extracts_schedule_venue_and_pillar():
    row = parse_entry(2, "ASEAN SEOM Retreat 2026 10-11 December 2025 Boracay, Philippines AEC")
    assert row == {
        "nomor_pada_kalender": 2,
        "pertemuan": "ASEAN SEOM Retreat 2026",
        "jadwal_menurut_sumber": "10-11 December 2025",
        "lokasi_menurut_sumber": "Boracay, Philippines",
        "pilar": "AEC",
    }


def test_parse_entry_keeps_tbc_and_quarter_schedules_verbatim():
    assert parse_entry(1, "Trade Fair 10-11 December 2025 (TBC) AEC")["jadwal_menurut_sumber"] == "10-11 December 2025 (TBC)"
    quarter = parse_entry(4, "Sub-Regional Meeting Q3 The Philippines APSC")
    assert quarter["jadwal_menurut_sumber"] == "Q3"
    assert quarter["lokasi_menurut_sumber"] == "The Philippines"
    deferred = parse_entry(6, "RCEP Leaders Summit Defer to DFA on the appropriate date Metro Manila, Philippines AEC")
    assert deferred["jadwal_menurut_sumber"] == "Defer to DFA on the appropriate date"


def test_parse_entry_leaves_blank_cells_empty():
    row = parse_entry(5, "37th Meeting of ASEAN Senior Officials on Environment (ASOEN)")
    assert row["jadwal_menurut_sumber"] is None and row["pilar"] is None


def test_parse_calendar_text_end_to_end():
    rows = parse_calendar_text(TEXT)
    assert len(rows) == 7
    assert rows[0]["jadwal_menurut_sumber"] == "10-11 December 2025 (TBC)"
    assert rows[1]["pilar"] == "AEC" and rows[1]["lokasi_menurut_sumber"] == "Boracay, Philippines"
    assert rows[2]["jadwal_menurut_sumber"] == "8 January 2026" and rows[2]["lokasi_menurut_sumber"] == "Virtual"
    assert rows[6]["pilar"] == "Cross-Pillar" and rows[6]["jadwal_menurut_sumber"] == "8 January 2026"
    assert Record(**rows[0]).nomor_pada_kalender == 1


def test_find_calendar_links_picks_notional_calendar_pdfs():
    html = (
        '<a href="/wp-content/uploads/2026/ASEAN-Notional-Calendar-2026.pdf">Notional Calendar</a>'
        '<a href="/wp-content/uploads/other.pdf">Annual report</a>'
    )
    assert find_calendar_links(html, "https://asean.org/events-calendar/") == [
        "https://asean.org/wp-content/uploads/2026/ASEAN-Notional-Calendar-2026.pdf"
    ]


def test_extractor_raises_when_nothing_parsed(monkeypatch):
    monkeypatch.setattr(Extractor, "_load_pdf", lambda self: b"%PDF")
    monkeypatch.setattr(ext, "pdf_text", lambda content: "no numbered rows here")
    with pytest.raises(SourceUnavailable):
        list(Extractor({}).extract())


WRAPPED = """ASEAN 2026 PUBLIC NOTIONAL CALENDAR as of 8 January 2026
No. of
Meetings Meeting/ Specific Activity Date  Venue Pillar
NOVEMBER 2026
1 ASEAN Summit 28-30 November 2026 Manila AEC
DECEMBER
2 Closing Meeting of the Working Group 14
December 2026
Virtual AEC
3 Leaders Meeting 3 September2026 Manila APSC
4 Retreat 1-3 October 2026 (3 days incl. travel) (TBC) Cebu ASCC
"""


def test_wrapped_year_is_not_taken_for_a_month_heading_and_glued_months_are_spaced():
    rows = parse_calendar_text(WRAPPED)
    assert [r["nomor_pada_kalender"] for r in rows] == [1, 2, 3, 4]
    assert rows[1]["jadwal_menurut_sumber"] == "14 December 2026"
    assert rows[1]["pilar"] == "AEC" and rows[1]["lokasi_menurut_sumber"] == "Virtual"
    assert rows[2]["jadwal_menurut_sumber"] == "3 September 2026"
    assert rows[3]["jadwal_menurut_sumber"].startswith("1-3 October 2026")
    assert rows[3]["lokasi_menurut_sumber"] == "Cebu" and rows[3]["pilar"] == "ASCC"
