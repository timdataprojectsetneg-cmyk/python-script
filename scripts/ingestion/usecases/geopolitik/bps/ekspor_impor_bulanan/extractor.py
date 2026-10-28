"""Extractor for BPS monthly export/import totals (https://www.bps.go.id/id/exim).

The BPS site is a Next.js app: the "Data Ekspor Impor" page fills its monthly
summary table through a *server action* (``summaryMonthlyExim``) that is POSTed
to the page URL. The action id is a build hash, so it is discovered from the
page's JavaScript chunks on every run (``PARAMS={"action_id": "..."}`` pins it).
"""

from __future__ import annotations

import json
import logging
import re
from datetime import date
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urlsplit

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.bps.go.id/id/exim"
DEFAULT_FIRST_YEAR = 2020
ACTION_NAME = "summaryMonthlyExim"
_ACTION_RE = re.compile(r'createServerReference\)\("([0-9a-f]{20,})"[^)]*?"' + ACTION_NAME + r'"\)')
_CHUNK_RE = re.compile(r'/_next/static/chunks/[^"\'\s\\]+?\.js')
_CHUNK_MAP_RE = re.compile(r'"static/chunks/"\+e\+"\."\+\(\{(.*?)\}\)\[e\]')


def parse_years(value: Any, default_first: int = DEFAULT_FIRST_YEAR) -> List[int]:
    """``YEARS`` as ``2023,2024`` or ``2020-2026``; default: first year..current."""
    text = str(value or "").strip()
    if not text:
        return list(range(default_first, date.today().year + 1))
    years: List[int] = []
    for part in re.split(r"[;,]", text):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            years.extend(range(int(start), int(end) + 1))
        else:
            years.append(int(part))
    return sorted(set(years))


def parse_action_response(text: str) -> Dict[str, Any]:
    """Pull the ``{"status":..,"response":..}`` payload out of an RSC action reply."""
    for line in text.splitlines():
        _, _, body = line.partition(":")
        if not body.startswith("{"):
            continue
        try:
            payload = json.loads(body)
        except ValueError:
            continue
        if isinstance(payload, dict) and "status" in payload:
            return payload
    raise SourceUnavailable("BPS exim: unrecognised server-action response")


def _to_float(value: Any) -> Optional[float]:
    if value in (None, "", "-"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def rows_to_records(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Map BPS summary rows (year, month, eval, enetwt, ival, inetwt) to dictionary fields."""
    records = []
    for row in rows:
        year, month = row.get("year"), row.get("month")
        if not year or not month:
            continue
        records.append(
            {
                "periode": f"{int(year):04d}-{int(month):02d}",
                "nilai_ekspor": _to_float(row.get("eval")),
                "berat_ekspor": _to_float(row.get("enetwt")),
                "nilai_impor": _to_float(row.get("ival")),
                "berat_impor": _to_float(row.get("inetwt")),
            }
        )
    return records


class Extractor(BaseExtractor):
    """BPS exim monthly summary via the Next.js server action."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url") or DEFAULT_URL
        self.years = parse_years(config.get("years") or config.get("tahun"))
        self.action_id = self._param("action_id")
        self.host = urlsplit(self.url).netloc or "www.bps.go.id"

    def _param(self, key: str) -> Optional[str]:
        params = self.config.get("params")
        if isinstance(params, str) and params.strip():
            try:
                params = json.loads(params)
            except ValueError as exc:
                raise ConfigError(f"PARAMS must be a JSON object: {exc}") from exc
        if isinstance(params, dict):
            return params.get(key)
        return None

    def _origin(self) -> str:
        parts = urlsplit(self.url)
        return f"{parts.scheme}://{parts.netloc}"

    def discover_action_id(self) -> str:
        """Find the ``summaryMonthlyExim`` server-action id in the page's JS chunks."""
        html = self.http.get(self.url, timeout=45).text
        chunks = list(dict.fromkeys(_CHUNK_RE.findall(html)))
        runtime = next((c for c in chunks if "/webpack-" in c), None)
        lazy: List[str] = []
        if runtime:
            js = self.http.get(self._origin() + runtime, timeout=45).text
            match = _CHUNK_MAP_RE.search(js)
            if match:
                lazy = [
                    f"/_next/static/chunks/{cid}.{h}.js"
                    for cid, h in re.findall(r'(\d+):"([0-9a-f]{16})"', match.group(1))
                ]
        for path in dict.fromkeys(lazy + chunks):
            try:
                js = self.http.get(self._origin() + path, timeout=45).text
            except SourceUnavailable:
                continue
            found = _ACTION_RE.search(js)
            if found:
                return found.group(1)
        raise SourceUnavailable(
            f"BPS exim: server action '{ACTION_NAME}' not found on {self.url}; "
            'the site may have changed (pin it with PARAMS={"action_id": "..."})'
        )

    def fetch_year(self, year: int) -> List[Dict[str, Any]]:
        resp = self.http.post(
            self.url,
            headers={
                "Next-Action": self.action_id,
                "Content-Type": "text/plain;charset=UTF-8",
                "Accept": "text/x-component",
            },
            data=json.dumps([self.host, "id", year]),
            timeout=60,
        )
        payload = parse_action_response(resp.text)
        if not payload.get("status"):
            raise SourceUnavailable(f"BPS exim {year}: {payload.get('msg') or 'action failed'}")
        body = payload.get("response") or {}
        if body.get("status") == "Error":
            raise SourceUnavailable(f"BPS exim {year}: {body.get('message')}")
        if body.get("data-availability") != "available":
            return []
        return rows_to_records(body.get("data") or [])

    def extract(self) -> Iterator[Dict[str, Any]]:
        if not self.action_id:
            self.action_id = self.discover_action_id()
            logger.info("BPS exim server action id: %s", self.action_id)
        total = 0
        for year in self.years:
            try:
                records = self.fetch_year(year)
            except SourceUnavailable as exc:
                # a year outside BPS's supported range is not fatal
                logger.warning("BPS exim %s skipped: %s", year, exc)
                continue
            logger.info("BPS exim %s: %d months", year, len(records))
            for record in records:
                total += 1
                yield record
        if total == 0:
            raise SourceUnavailable(f"BPS exim: no monthly data returned for years {self.years}")
