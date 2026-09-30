"""Generic Excel extractor.

Handles three patterns:
1. A ``download_url`` already resolved by a previous pipeline step.
2. A direct Excel URL.
3. A landing page HTML that embeds a download link, discovered via a CSS
   selector supplied in config (``DOWNLOAD_SELECTOR``) — the selector is
   deliberately not hardcoded here because it differs per use case.
"""

from __future__ import annotations

import re
from io import BytesIO
from typing import Any, Dict, Iterator, List
from urllib.parse import unquote

from bs4 import BeautifulSoup

from ...exceptions import ConfigError, SourceUnavailable
from ..base.extractor import BaseExtractor
from .utils import parse_fields


class ExcelExtractor(BaseExtractor):
    def _selector(self) -> str:
        selector = self.config.get("download_selector")
        if not selector:
            raise ConfigError(
                "Missing DOWNLOAD_SELECTOR for Excel extraction. Set it in the source "
                "extractor or via {USECASE}__{SOURCE}__EXCEL__DOWNLOAD_SELECTOR."
            )
        return selector

    def _fetch_page_html(self) -> str:
        selector = self._selector()
        resp = self.http.get(self.url, timeout=30)
        return resp.text

    def _find_download_url(self, html: str) -> str:
        selector = self._selector()
        soup = BeautifulSoup(html, "html.parser")
        container = soup.find("div", class_=selector) or soup.select_one(f".{selector}")
        if container:
            link = container.find("a", href=True)
            if link:
                return link["href"]

        # Fallback: the selector may differ per page — scan for any download link.
        candidate = self._scan_download_link(soup, html)
        if candidate:
            return candidate

        if "Web Page Blocked" in html or "Web Page Blocked!" in html:
            raise SourceUnavailable(
                "The site returned a 'Web Page Blocked' page (network/firewall filter). "
                "Run from an allowed network, or set "
                "{USECASE}__{SOURCE}__EXCEL__DOWNLOAD_URL to the file URL."
            )
        if 'id="root"' in html:
            raise SourceUnavailable(
                f"Download container '{selector}' not found and no download link was found; "
                "the page looks like a JavaScript SPA. Set {USECASE}__{SOURCE}__EXCEL__DOWNLOAD_URL."
            )
        raise SourceUnavailable(f"Download container not found for selector: {selector}")

    @staticmethod
    def _scan_download_link(soup: BeautifulSoup, html: str) -> str | None:
        """Find a plausible download URL anywhere on the page."""
        best: str | None = None
        for anchor in soup.find_all("a", href=True):
            href = str(anchor["href"])
            lowered = href.lower()
            if "files/data" in lowered or lowered.endswith((".xlsx", ".xls", ".xlsm")):
                return href
            if "download" in lowered and best is None:
                best = href
        for node in soup.find_all(attrs={"data-href": True}):
            best = best or str(node["data-href"])
        # Last resort: any absolute xlsx URL anywhere in the HTML (e.g. embedded JSON).
        match = re.search(r"https?://[^\"'<>\s]+?\.(?:xlsx|xls|xlsm)", html)
        return best or (match.group(0) if match else None)

    def _resolve_download_url(self) -> str:
        from_step = self.config.get("download_url")
        if from_step:
            return str(from_step)
        url = self.url
        if url.lower().endswith((".xlsx", ".xls", ".xlsm")):
            return url
        return self._find_download_url(self._fetch_page_html())

    def _download(self, url: str):
        """Download the file. Some portals keep double-encoded (``%2520``) paths,
        others expect a decoded path — try the URL as-is first, then decoded."""
        try:
            return self.http.get(url, timeout=120)
        except SourceUnavailable:
            decoded = unquote(url)
            if decoded != url:
                return self.http.get(decoded, timeout=120)
            raise

    def _parse_excel(self, content: bytes) -> List[Dict[str, Any]]:
        import pandas as pd

        sheet = self.config.get("sheet")
        header_row = int(self.config.get("header_row", 0) or 0)
        frames = pd.read_excel(
            BytesIO(content),
            sheet_name=sheet if sheet else 0,
            header=header_row,
            engine="openpyxl",
        )
        if isinstance(frames, dict):
            records: List[Dict[str, Any]] = []
            for frame in frames.values():
                records.extend(frame.to_dict(orient="records"))
            return records
        return frames.to_dict(orient="records")

    def _apply_column_map(self, record: Dict[str, Any]) -> Dict[str, Any]:
        field_map = parse_fields(self.config.get("columns"))
        if not field_map:
            return record
        mapped: Dict[str, Any] = {}
        for field in field_map:
            label = field.get("label") or field.get("source")
            target = field.get("name") or field.get("target") or label
            if label in record:
                mapped[target] = record.get(label)
            elif target in record:
                mapped[target] = record.get(target)
        for key, value in record.items():
            mapped.setdefault(key, value)
        return mapped

    def extract(self) -> Iterator[Dict[str, Any]]:
        download_url = self._resolve_download_url()
        resp = self._download(download_url)
        for record in self._parse_excel(resp.content):
            yield self._apply_column_map(record)
