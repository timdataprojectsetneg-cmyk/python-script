"""Tests for dynamic (JS-rendered) page support."""

from ingestion.core.extractors.dynamic import is_dynamic, is_missing_browser_error, install_hint
from ingestion.core.extractors.excel_extractor import ExcelExtractor
import ingestion.core.extractors.excel_extractor as excel_module


def test_is_dynamic():
    assert is_dynamic(True)
    assert is_dynamic("true")
    assert is_dynamic("YES")
    assert is_dynamic("1")
    assert not is_dynamic(False)
    assert not is_dynamic("false")
    assert not is_dynamic(None)


def test_missing_browser_error_detection():
    assert is_missing_browser_error(
        Exception("BrowserType.launch: Executable doesn't exist at /c/ms-playwright/chromium/x")
    )
    assert is_missing_browser_error(Exception("Please run the following command: playwright install"))
    assert not is_missing_browser_error(Exception("net::ERR_NAME_NOT_RESOLVED"))


def test_install_hint_mentions_interpreter_and_command():
    hint = install_hint()
    assert "playwright install chromium" in hint
    assert "Interpreter" in hint


def test_dynamic_renders_and_finds_link(monkeypatch):
    rendered = '<div class="bg-satudata-800"><a href="http://files/a.xlsx">Download</a></div>'
    monkeypatch.setattr(excel_module, "render_html", lambda url, wait_for_selector=None: rendered)

    extractor = ExcelExtractor(
        {
            "usecase": "u",
            "source": "s",
            "access": "excel",
            "url": "https://satudata.kemnaker.go.id/data/kumpulan-data/3674",
            "download_selector": "bg-satudata-800",
            "dynamic": True,
        }
    )
    assert extractor._resolve_download_url() == "http://files/a.xlsx"
