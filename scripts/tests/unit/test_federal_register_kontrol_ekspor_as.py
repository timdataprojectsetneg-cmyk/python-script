"""Offline tests for Federal Register BIS rules (Kontrol Ekspor AS)."""

from datetime import date

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.federal_register.kontrol_ekspor_as.extractor import (
    Extractor,
    document_number_from_url,
    parse_result,
)
from ingestion.usecases.geopolitik.federal_register.kontrol_ekspor_as.models import Record

RULE = {
    "title": "Export Administration Regulations: Entity List additions",
    "publication_date": "2026-10-01",
    "effective_on": "2026-10-01",
    "html_url": "https://www.federalregister.gov/documents/2026/10/01/2026-12345/export-administration-regulations",
}
CORRECTION = {**RULE, "html_url": "https://www.federalregister.gov/documents/2026/10/05/C1-2026-12345/correction"}


class StubHttp:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def get(self, url, params=None, **kwargs):
        self.calls.append((url, params))
        payload = self.pages[len(self.calls) - 1]

        class Resp:
            def json(self_inner):
                return payload

        return Resp()


def test_document_number_from_url():
    assert document_number_from_url(RULE["html_url"]) == "2026-12345"
    assert document_number_from_url("https://example.com/x") is None
    assert document_number_from_url(None) is None


def test_parse_result_and_record():
    row = parse_result(RULE)
    assert row["document_number"] == "2026-12345" and row["is_correction"] is False
    record = Record(**row)
    assert record.publication_date == date(2026, 10, 1)


def test_parse_result_flags_correction_and_skips_unknown():
    assert parse_result(CORRECTION)["is_correction"] is True
    assert parse_result({"title": "x", "html_url": "https://example.com"}) is None


def test_extractor_params_and_pagination():
    extractor = Extractor(
        {"usecase": "geopolitik", "url": "https://www.federalregister.gov/api/v1/documents", "page_size": 1}
    )
    extractor.http = StubHttp(
        [
            {"results": [RULE], "total_pages": 2},
            {"results": [CORRECTION], "total_pages": 2},
        ]
    )
    rows = list(extractor.extract())
    assert [r["document_number"] for r in rows] == ["2026-12345", "C1-2026-12345"]
    url, params = extractor.http.calls[0]
    assert url.endswith("/documents.json")
    assert params["conditions[agencies][]"] == "industry-and-security-bureau"
    assert params["conditions[type][]"] == "RULE" and params["order"] == "newest"


def test_missing_results_raises():
    extractor = Extractor({"usecase": "geopolitik"})
    extractor.http = StubHttp([{"error": "x"}])
    with pytest.raises(SourceUnavailable):
        list(extractor.extract())


def test_no_page_cap_and_restart_after_api_window():
    extractor = Extractor({"usecase": "geopolitik", "page_size": 5000})
    assert extractor.max_pages is None
    older = {**RULE, "publication_date": "2020-01-01",
             "html_url": "https://www.federalregister.gov/documents/2020/01/01/2020-00001/old"}
    extractor.http = StubHttp(
        [
            {"results": [RULE], "total_pages": 3},
            {"results": [RULE], "total_pages": 3},
            {"results": [older], "total_pages": 1},
        ]
    )
    rows = list(extractor.extract())
    assert [r["document_number"] for r in rows] == ["2026-12345", "2020-00001"]
    assert extractor.http.calls[2][1]["conditions[publication_date][lte]"] == "2026-10-01"
    assert extractor.http.calls[2][1]["page"] == 1
