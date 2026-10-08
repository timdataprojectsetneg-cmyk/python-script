"""Tests for SharePoint file resolution by item id and by path."""

import pytest

from ingestion.exceptions import ConfigError, ItemNotFound, SourceUnavailable
from ingestion.sharepoint.client import SharePointClient, is_item_id


@pytest.fixture
def client():
    return SharePointClient()


def test_is_item_id():
    assert is_item_id("0F1E2D3C-4B5A-6978-8C9D-0E1F2A3B4C5D")
    assert is_item_id("01ABCDEF23GHIJKL45MNOPQR")
    assert not is_item_id("Folder/File.xlsx")
    assert not is_item_id("Available Data Source per Usecase.xlsx")
    assert not is_item_id("")


def test_get_content_dispatch_path(client, monkeypatch):
    calls = {}

    def fake_path(ref):
        calls["path"] = ref
        return b"p"

    def fake_id(iid):
        calls["id"] = iid
        return b"i"

    monkeypatch.setattr(client, "download_file", fake_path)
    monkeypatch.setattr(client, "download_file_by_id", fake_id)

    assert client.get_content("Folder/Data Dictionary.xlsx") == b"p"
    assert calls["path"] == "Folder/Data Dictionary.xlsx"

    assert client.get_content("01ABCDEF23GHIJKL45MNOPQR") == b"i"
    assert calls["id"] == "01ABCDEF23GHIJKL45MNOPQR"

    # Explicit id: prefix forces id even when the value contains a slash.
    assert client.get_content("id:01ABCDEF/GHIJKL45MNOPQR") == b"i"
    assert calls["id"] == "01ABCDEF/GHIJKL45MNOPQR"


def test_download_file_by_id_uses_site(client, monkeypatch):
    captured = {}

    def fake_fetch(url):
        captured["url"] = url
        return b"content"

    client.site_id = "contoso.sharepoint.com,sites/SetnegTeam"
    client.drive_id = "b!DriveId"
    monkeypatch.setattr(client, "_fetch", fake_fetch)

    assert client.download_file_by_id("01FILEID") == b"content"
    assert captured["url"] == (
        "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com,sites/SetnegTeam/"
        "drive/items/01FILEID/content"
    )


def test_item_url(client):
    client.site_id = "contoso.sharepoint.com,sites/SetnegTeam"
    assert client.item_url("01FILEID") == (
        "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com,sites/SetnegTeam/"
        "drive/items/01FILEID"
    )


def test_download_file_by_id_falls_back_to_drive(client, monkeypatch):
    captured = {}

    def fake_fetch(url):
        captured["url"] = url
        return b"c"

    client.site_id = None
    client.drive_id = "b!DriveId"
    monkeypatch.setattr(client, "_fetch", fake_fetch)

    client.download_file_by_id("01FILEID")
    assert captured["url"] == (
        "https://graph.microsoft.com/v1.0/drives/b%21DriveId/items/01FILEID/content"
    )


def test_download_file_by_id_requires_drive_or_site(client):
    client.drive_id = None
    client.site_id = None
    with pytest.raises(ConfigError):
        client.download_file_by_id("01FILEID")


def test_catalog_ref_precedence(client):
    client.file_id = "01FILEID"
    client.catalog_file_id = "01CATALOGID"
    client.catalog_path = "Folder/Catalog.xlsx"
    assert client.catalog_ref() == "01FILEID"
    assert client.catalog_ref("id:OVERRIDE") == "id:OVERRIDE"
    client.file_id = None
    assert client.catalog_ref() == "01CATALOGID"
    client.catalog_file_id = None
    assert client.catalog_ref() == "Folder/Catalog.xlsx"


def test_dictionary_ref_builds_per_sheet_path(client):
    name = "Data Dictionary - Ketenagakerjaan - Hubungan Industrial dan Pengupahan.xlsx"
    ref = client.dictionary_ref(name, "Ketenagakerjaan")
    assert ref == (
        "Sitroom-2026/PROJECT/DATA/1 - Discover/Data Dictionary - Ketenagakerjaan/" + name
    )
    # Item ids and explicit paths pass through unchanged.
    assert client.dictionary_ref("01ABCDEF23GHIJKL45MNOPQR", "X") == "01ABCDEF23GHIJKL45MNOPQR"
    assert client.dictionary_ref("Folder/File.xlsx", "X") == "Folder/File.xlsx"
    assert client.dictionary_ref("", "X") is None


def test_read_matrix(client, monkeypatch):
    import io

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "S"
    ws.append(["a", "b"])
    ws.append([1, 2])
    buffer = io.BytesIO()
    wb.save(buffer)
    monkeypatch.setattr(client, "get_content", lambda ref: buffer.getvalue())

    matrix = client.read_matrix("X", "S")
    assert matrix[0] == ["a", "b"]
    assert matrix[1] == [1, 2]


def test_children_url(client):
    client.site_id = "contoso.sharepoint.com,sites/SetnegTeam"
    client.drive_id = None
    assert client._children_url("Folder/Sub") == (
        "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com,sites/SetnegTeam/"
        "drive/root:/Folder/Sub:/children"
    )
    assert client._children_url("") == (
        "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com,sites/SetnegTeam/"
        "drive/root/children"
    )
    client.site_id = None
    client.drive_id = "b!DriveId"
    assert client._children_url("Folder") == (
        "https://graph.microsoft.com/v1.0/drives/b%21DriveId/root:/Folder:/children"
    )


def test_match_child_prefers_exact_then_shortest_suffix(client):
    children = [
        {"name": "1. Foo.xlsx", "id": "a"},
        {"name": "Foo.xlsx", "id": "b"},
    ]
    assert client._match_child(children, "Foo.xlsx")["id"] == "b"
    assert client._match_child(children, "Bar.xlsx") is None
    assert client._match_child(children, "") is None

    prefixed_only = [
        {"name": "10. Data Dictionary - Foo.xlsx", "id": "a"},
        {"name": "2. Data Dictionary - Foo.xlsx", "id": "b"},
    ]
    assert client._match_child(prefixed_only, "Data Dictionary - Foo.xlsx")["id"] == "b"


def test_download_file_falls_back_to_suffix_match(client, monkeypatch):
    client.drive_id = None
    client.site_id = "contoso.sharepoint.com,sites/SetnegTeam"
    calls = {}

    def fake_fetch(url):
        calls["fetched"] = url
        raise ItemNotFound("SharePoint item not found")

    def fake_children(folder):
        calls["folder"] = folder
        return [
            {"name": "1. Data Dictionary.xlsx", "id": "01PREFIXED"},
            {"name": "Unrelated.xlsx", "id": "01OTHER"},
        ]

    def fake_by_id(iid):
        calls["by_id"] = iid
        return b"content"

    monkeypatch.setattr(client, "_fetch", fake_fetch)
    monkeypatch.setattr(client, "list_children", fake_children)
    monkeypatch.setattr(client, "download_file_by_id", fake_by_id)

    assert client.download_file("Folder/Data Dictionary.xlsx") == b"content"
    assert calls["folder"] == "Folder"
    assert calls["by_id"] == "01PREFIXED"


def test_download_file_reraises_without_match(client, monkeypatch):
    client.drive_id = None
    client.site_id = "contoso.sharepoint.com,sites/SetnegTeam"

    def fake_fetch(url):
        raise ItemNotFound("SharePoint item not found")

    monkeypatch.setattr(client, "_fetch", fake_fetch)
    monkeypatch.setattr(
        client, "list_children", lambda folder: [{"name": "Nope.xlsx", "id": "x"}]
    )

    with pytest.raises(SourceUnavailable):
        client.download_file("Folder/Data Dictionary.xlsx")


def test_download_file_does_not_fall_back_on_non_404(client, monkeypatch):
    """Only a 404 (ItemNotFound) should trigger the suffix fallback."""
    client.drive_id = None
    client.site_id = "contoso.sharepoint.com,sites/SetnegTeam"
    called = {"children": False}

    def fake_fetch(url):
        raise SourceUnavailable("SharePoint download failed (503)")

    def fake_children(folder):
        called["children"] = True
        return []

    monkeypatch.setattr(client, "_fetch", fake_fetch)
    monkeypatch.setattr(client, "list_children", fake_children)

    with pytest.raises(SourceUnavailable):
        client.download_file("Folder/Data Dictionary.xlsx")
    assert called["children"] is False


