"""Tests for SpreadsheetClient hyperlink capture and dictionary link resolution."""

from ingestion.catalog.metadata_parser import parse_catalog_row
from ingestion.spreadsheet.client import SpreadsheetClient

GOOGLE_URL = (
    "https://docs.google.com/spreadsheets/d/1-2qflYSVPHCOp20JlOE7FmeSi8hLneTxaV_zIAgdwF0"
    "/edit?gid=5#gid=5"
)


class _Exec:
    def __init__(self, payload=None, error=None):
        self._payload = payload
        self._error = error

    def execute(self):
        if self._error:
            raise self._error
        return self._payload


class _FakeService:
    """Minimal Sheets API double: values.get, grid get, and metadata get."""

    def __init__(self, matrix, row_links=None, tabs=None, gids=None, meta_error=None):
        self.matrix = matrix
        self.row_links = row_links or []
        self.tabs = tabs or []
        self.gids = gids or []
        self.meta_error = meta_error

    def spreadsheets(self):
        return self

    def values(self):
        return self

    def get(self, **kwargs):
        if "range" in kwargs:  # values().get
            return _Exec({"values": self.matrix})
        if kwargs.get("includeGridData"):  # grid data (hyperlinks)
            row_data = [{"values": [{} for _ in row]} for row in self.matrix]
            for row_index, links in enumerate(self.row_links):
                if row_index >= len(row_data):
                    continue
                cells = row_data[row_index]["values"]
                for col, url in links.items():
                    while len(cells) <= col:
                        cells.append({})
                    cells[col] = {"hyperlink": url}
            return _Exec({"sheets": [{"data": [{"rowData": row_data}]}]})
        if "sheetId" in str(kwargs.get("fields", "")):  # gid -> tab index
            if self.meta_error:
                return _Exec(error=self.meta_error)
            return _Exec(
                {
                    "sheets": [
                        {"properties": {"sheetId": gid, "index": index}}
                        for index, gid in enumerate(self.gids)
                    ]
                }
            )
        return _Exec(
            {
                "sheets": [
                    {"properties": {"title": title, "index": index}}
                    for index, title in enumerate(self.tabs)
                ]
            }
        )


def _client(monkeypatch, **fake_kwargs):
    monkeypatch.setenv("SPREADSHEET__FILE_ID", "catalogWorkbookId0000000")
    client = SpreadsheetClient()
    service = _FakeService(**fake_kwargs)
    monkeypatch.setattr(client, "_api", lambda: service)
    return client


def test_read_sheet_attaches_hyperlink_under_links(monkeypatch):
    matrix = [
        ["No", "Source Name", "Data Dictionary"],
        ["1", "Direktori Putusan PHI", "Dict.xlsx"],
    ]
    client = _client(monkeypatch, matrix=matrix, row_links=[{}, {2: GOOGLE_URL}])

    rows = client.read_sheet("ref", "Sheet1", header_hints=["Source Name"])

    assert len(rows) == 1
    assert rows[0]["_links"] == {"Data Dictionary": GOOGLE_URL}
    parsed = parse_catalog_row(rows[0])
    assert parsed["data_dictionary_link"] == GOOGLE_URL


def test_read_sheet_uses_text_format_link(monkeypatch):
    matrix = [["Source Name"], ["A"]]
    service = _FakeService(matrix=matrix)
    original_get = service.get

    def get(**kwargs):
        if kwargs.get("includeGridData"):
            return _Exec(
                {
                    "sheets": [
                        {
                            "data": [
                                {
                                    "rowData": [
                                        {"values": [{}]},
                                        {
                                            "values": [
                                                {
                                                    "userEnteredFormat": {
                                                        "textFormat": {"link": {"uri": GOOGLE_URL}}
                                                    }
                                                }
                                            ]
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                }
            )
        return original_get(**kwargs)

    monkeypatch.setenv("SPREADSHEET__FILE_ID", "catalogWorkbookId0000000")
    client = SpreadsheetClient()
    monkeypatch.setattr(client, "_api", lambda: service)
    monkeypatch.setattr(service, "get", get)

    rows = client.read_sheet("ref", "Sheet1", header_hints=["Source Name"])
    assert rows[0]["_links"] == {"Source Name": GOOGLE_URL}


def test_resolve_dictionary_link(monkeypatch):
    client = _client(monkeypatch, matrix=[])
    assert client.resolve_dictionary_link(GOOGLE_URL, "Harmonisasi") == (
        "1-2qflYSVPHCOp20JlOE7FmeSi8hLneTxaV_zIAgdwF0"
    )
    assert client.resolve_dictionary_link("01ABCDEF23GHIJKL45MNOP", "X") == (
        "01ABCDEF23GHIJKL45MNOP"
    )
    assert client.resolve_dictionary_link("", "X") is None
    # A bare name falls back to the catalog workbook.
    assert client.resolve_dictionary_link("Dict.xlsx", "X") == "catalogWorkbookId0000000"


def test_link_sheet_hint_maps_gid_to_index(monkeypatch):
    client = _client(monkeypatch, matrix=[], gids=[0, 5, 7])
    assert client.link_sheet_hint(GOOGLE_URL) == 1
    assert client.link_sheet_hint("https://docs.google.com/spreadsheets/d/ID/edit") is None
    assert client.link_sheet_hint("https://example.com/x") is None
    assert client.link_sheet_hint("") is None


def test_link_sheet_hint_is_best_effort_on_error(monkeypatch):
    client = _client(monkeypatch, matrix=[], gids=[5], meta_error=RuntimeError("403"))
    assert client.link_sheet_hint(GOOGLE_URL) is None
