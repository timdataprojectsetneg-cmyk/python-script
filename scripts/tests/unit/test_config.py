"""Unit tests for config and helpers."""

import pytest

from ingestion.config import env_key, load_config
from ingestion.exceptions import ConfigError, SourceUnavailable
from ingestion.core.extractors.utils import decode_url, get_path


def test_env_key_format():
    assert env_key("ketenagakerjaan", "kemnaker", "kasus_perselisihan", "url") == (
        "KETENAGAKERJAAN__KEMNAKER__KASUS_PERSELISIHAN__URL"
    )


def test_load_config_missing_url(monkeypatch):
    monkeypatch.delenv("GHOST__PUB__SRC__URL", raising=False)
    with pytest.raises(ConfigError):
        load_config("ghost", "pub", "src")


def test_load_config_reads_env(monkeypatch):
    monkeypatch.setenv("DEMO__PUB__SRC__URL", "https://example.com")
    cfg = load_config("demo", "pub", "src")
    assert cfg["url"] == "https://example.com"
    assert cfg["target"] == "postgres"


def test_load_config_reads_download_url_override(monkeypatch):
    monkeypatch.setenv("KETENAGAKERJAAN__KEMNAKER__KASUS_PERSELISIHAN__URL", "https://satudata/page")
    monkeypatch.setenv("KETENAGAKERJAAN__KEMNAKER__KASUS_PERSELISIHAN__DOWNLOAD_URL", "https://x/a.xlsx")
    cfg = load_config("ketenagakerjaan", "kemnaker", "kasus_perselisihan")
    assert cfg["download_url"] == "https://x/a.xlsx"


def test_excel_uses_download_url_override_without_network():
    from ingestion.core.extractors.excel_extractor import ExcelExtractor

    extractor = ExcelExtractor(
        {
            "usecase": "u",
            "source": "s",
            "access": "excel",
            "url": "https://page",
            "download_url": "https://x/a.xlsx",
        }
    )
    assert extractor._resolve_download_url() == "https://x/a.xlsx"


def test_excel_keeps_raw_href():
    from ingestion.core.extractors.excel_extractor import ExcelExtractor

    extractor = ExcelExtractor(
        {
            "usecase": "u",
            "source": "s",
            "access": "excel",
            "url": "https://page",
            "download_selector": "bg-satudata-800",
        }
    )
    html = '<div class="bg-satudata-800"><a href="https://x/7.%2520PPHI.xlsx">d</a></div>'
    assert extractor._find_download_url(html) == "https://x/7.%2520PPHI.xlsx"


def test_excel_download_falls_back_to_decoded(monkeypatch):
    import ingestion.core.extractors.excel_extractor as mod

    extractor = mod.ExcelExtractor(
        {"usecase": "u", "source": "s", "access": "excel", "url": "https://page"}
    )
    calls = []

    class Response:
        content = b"xlsx-bytes"

    def fake_get(url, timeout=0):
        calls.append(url)
        if "%2520" in url:
            raise SourceUnavailable("404")
        return Response()

    monkeypatch.setattr(extractor.http, "get", fake_get)
    resp = extractor._download("https://x/7.%2520PPHI.xlsx")
    assert resp.content == b"xlsx-bytes"
    assert calls == ["https://x/7.%2520PPHI.xlsx", "https://x/7.%20PPHI.xlsx"]


def test_target_defaults_to_postgres(monkeypatch):
    monkeypatch.setenv("DEMO__PUB__SRC__URL", "https://example.com")
    cfg = load_config("demo", "pub", "src")
    assert cfg["target"] == "postgres"


def test_target_env_override(monkeypatch):
    monkeypatch.setenv("DEMO__PUB__SRC__URL", "https://example.com")
    monkeypatch.setenv("DEMO__PUB__SRC__TARGET", "none")
    cfg = load_config("demo", "pub", "src")
    assert cfg["target"] == "none"


def test_load_config_optional_url(monkeypatch):
    monkeypatch.delenv("GHOST__PUB__SRC__URL", raising=False)
    cfg = load_config("ghost", "pub", "src", require_url=False)
    assert cfg["source"] == "src"
    assert "access" not in cfg


def test_excel_extractor_requires_selector():
    from ingestion.core.extractors.excel_extractor import ExcelExtractor

    extractor = ExcelExtractor(
        {"usecase": "u", "source": "s", "access": "excel", "url": "https://x/page"}
    )
    with pytest.raises(ConfigError):
        extractor._find_download_url("<html><body></body></html>")


def test_spa_page_hint():
    from ingestion.core.extractors.excel_extractor import ExcelExtractor

    extractor = ExcelExtractor(
        {
            "usecase": "u",
            "source": "s",
            "access": "excel",
            "url": "https://x/page",
            "download_selector": "bg-satudata-800",
        }
    )
    with pytest.raises(SourceUnavailable) as err:
        extractor._find_download_url('<html><body><div id="root"></div></body></html>')
    assert "SPA" in str(err.value)


def _excel(selector="bg-satudata-800"):
    from ingestion.core.extractors.excel_extractor import ExcelExtractor

    return ExcelExtractor(
        {"usecase": "u", "source": "s", "access": "excel", "url": "https://p", "download_selector": selector}
    )


def test_find_download_url_generic_anchor_fallback():
    html = '<div id="root"><a href="https://x/satudata-public/2026/07/files/data/a.xlsx">Download .xlsx</a></div>'
    assert _excel()._find_download_url(html) == (
        "https://x/satudata-public/2026/07/files/data/a.xlsx"
    )


def test_find_download_url_embedded_in_html_fallback():
    html = '<div id="root"><script>window.__D__={"file":"https://x/files/data/b.xlsx"}</script></div>'
    assert _excel()._find_download_url(html) == "https://x/files/data/b.xlsx"


def test_blocked_page_message():
    html = "<html><body><h1>Web Page Blocked!</h1></body></html>"
    with pytest.raises(SourceUnavailable) as err:
        _excel()._find_download_url(html)
    assert "Blocked" in str(err.value)


def test_source_extractor_subclasses_generic():
    from ingestion.core.extractors.excel_extractor import ExcelExtractor
    from ingestion.usecases.ketenagakerjaan.kemnaker.kasus_perselisihan.extractor import (
        Extractor,
    )

    assert issubclass(Extractor, ExcelExtractor)
    assert Extractor({}).__class__.__module__.endswith("kasus_perselisihan.extractor")


def test_decode_url_double_encoding():
    encoded = "https://x/y_7.%2520PPHI%2520oleh%2520mediator.xlsx"
    assert decode_url(encoded) == "https://x/y_7.%20PPHI%20oleh%20mediator.xlsx"


def test_get_path():
    payload = {"result": [{"rows": [1, 2]}]}
    assert get_path(payload, "result[0].rows[1]") == 2
    assert get_path(payload, "missing.path") is None
