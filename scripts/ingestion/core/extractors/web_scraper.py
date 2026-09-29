"""Generic web scraper.

Static parsing uses BeautifulSoup. Dynamic (JS-rendered) pages can opt in to
Playwright via ``DYNAMIC=true``; Playwright is a soft dependency.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List

from bs4 import BeautifulSoup

from ..base.extractor import BaseExtractor
from .dynamic import is_dynamic, render_html
from .utils import parse_fields


class WebScraper(BaseExtractor):
    def _fetch_html(self) -> str:
        if is_dynamic(self.config.get("dynamic")):
            return self._fetch_dynamic()
        resp = self.http.get(self.url, timeout=60)
        return resp.text

    def _fetch_dynamic(self) -> str:  # pragma: no cover - requires playwright
        return render_html(self.url)

    def _extract_fields(self, node: Any) -> Dict[str, Any]:
        record: Dict[str, Any] = {}
        for field in parse_fields(self.config.get("fields")):
            name = field.get("name") or field.get("label")
            selector = field.get("selector")
            attr = field.get("attr") or field.get("attribute")
            if not name or not selector:
                continue
            target = node.select_one(selector)
            if target is None:
                record[name] = None
            elif attr:
                record[name] = target.get(attr)
            else:
                record[name] = target.get_text(strip=True)
        return record

    def extract(self) -> Iterator[Dict[str, Any]]:
        html = self._fetch_html()
        soup = BeautifulSoup(html, "html.parser")

        item_selector = self.config.get("item_selector")
        fields = parse_fields(self.config.get("fields"))

        if item_selector:
            for node in soup.select(item_selector):
                yield self._extract_fields(node)
            return

        if fields:
            yield self._extract_fields(soup)
            return

        # Fallback: yield the whole page text as a single record.
        text = soup.get_text(separator="\n", strip=True)
        yield {"url": self.url, "text": text}
