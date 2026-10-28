"""Offline tests for WTO ePing notifications."""

from datetime import date, timedelta

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.wto.eping_notifikasi.extractor import Extractor, parse_item
from ingestion.usecases.geopolitik.wto.eping_notifikasi.models import Record

ITEM = {
    "id": 123456,
    "area": "SPS",
    "notificationType": "Regular",
    "distributionDate": "2026-10-20T00:00:00",
    "commentDeadlineDate": "2026-12-19T00:00:00",
    "proposedAdoptionDate": None,
    "documentSymbol": " G/SPS/N/USA/3500 ",
    "notifyingMember": "United States of America",
    "notifyingMemberCode": "USA",
    "titlePlain": "Pesticide tolerances",
    "descriptionPlain": "Establishes tolerances.",
    "keywords": [{"name": "Pesticides"}, {"name": "Residues"}],
    "countriesAffected": [],
    "allTradingPartners": True,
    "conformStandardYes": False,
    "parentId": 99,
    "linkToNotification": "https://epingalert.org/en/Search?viewData=G%2FSPS%2FN%2FUSA%2F3500",
}


class StubHttp:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def get(self, url, params=None, **kwargs):
        self.calls.append(params)
        payload = self.pages[len(self.calls) - 1]

        class Resp:
            def json(self_inner):
                if isinstance(payload, Exception):
                    raise payload
                return payload

        return Resp()


def make(pages, **config):
    extractor = Extractor({"usecase": "geopolitik", **config})
    extractor.http = StubHttp(pages)
    return extractor


def test_parse_item_maps_dictionary_names_and_validates():
    row = parse_item(ITEM)
    assert row["id"] == "123456"
    assert row["distributiondate"] == "2026-10-20"
    assert row["documentsymbol"] == "G/SPS/N/USA/3500"
    assert row["keywords"] == "Pesticides; Residues"
    assert row["countriesaffected"] is None
    record = Record(**row)
    assert record.distributiondate == date(2026, 10, 20)
    assert record.alltradingpartners is True
    assert record.parentid == 99


def test_extract_paginates_until_total_count():
    pages = [{"items": [ITEM, ITEM], "totalCount": 3}, {"items": [ITEM], "totalCount": 3}]
    extractor = make(pages, page_size=2)
    assert len(list(extractor.extract())) == 3
    assert [c["page"] for c in extractor.http.calls] == [1, 2]


def test_build_params_default_window_and_url_query():
    default = make([], page_size=5).build_params(1)
    assert default["distributionDateFrom"] == (date.today() - timedelta(days=30)).isoformat()
    assert default["pageSize"] == 5 and "domainIds" not in default

    url = "https://epingalert.org/api/v1/azureSearch/getAll?distributionDateFrom=2026-01-01&domainIds=2&language=1"
    params = make([], url=url).build_params(1)
    assert params["distributionDateFrom"] == "2026-01-01"
    assert params["domainIds"] == ["2"]


def test_contract_changes_raise_source_unavailable():
    with pytest.raises(SourceUnavailable):
        list(make([{"unexpected": []}]).extract())
    with pytest.raises(SourceUnavailable):
        list(make([ValueError("not json")]).extract())


def test_extract_has_no_page_cap_by_default():
    pages = [{"items": [ITEM], "totalCount": 25} for _ in range(25)]
    extractor = make(pages, page_size=1)
    assert extractor.max_pages is None
    assert len(list(extractor.extract())) == 25


def test_lookback_zero_means_whole_history():
    extractor = make([], lookback_days=0)
    assert "distributionDateFrom" not in extractor.build_params(1)
