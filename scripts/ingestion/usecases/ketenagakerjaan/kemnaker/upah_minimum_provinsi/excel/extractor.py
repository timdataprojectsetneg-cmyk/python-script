"""Excel access — Upah Minimum Provinsi (UMP)."""

from __future__ import annotations

from typing import Any, Dict

from ......core.extractors.excel_extractor import ExcelExtractor

# CSS class of the download button on the satudata landing page (varies per source).
DOWNLOAD_SELECTOR = "bg-satudata-800"
# satudata is a React SPA, so the download link is rendered client-side.
DYNAMIC = True


class Extractor(ExcelExtractor):
    """Renders the satudata page, discovers the .xlsx link, and parses it."""

    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        merged.setdefault("download_selector", DOWNLOAD_SELECTOR)
        if merged.get("dynamic") is None:
            merged["dynamic"] = DYNAMIC
        super().__init__(merged)
