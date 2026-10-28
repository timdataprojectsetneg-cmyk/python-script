"""Shared helpers for sources backed by the UN Comtrade public preview API."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from ....core.base.http import HttpClient
from ....exceptions import SourceUnavailable

logger = logging.getLogger(__name__)

PARTNER_NAMES: Dict[int, str] = {
    0: "World",
    36: "Australia",
    156: "China",
    276: "Germany",
    356: "India",
    392: "Japan",
    410: "Rep. of Korea",
    458: "Malaysia",
    702: "Singapore",
    764: "Thailand",
    840: "USA",
}

RECORD_KEYS = (
    "period",
    "reporterCode",
    "flowCode",
    "partnerCode",
    "cmdCode",
    "primaryValue",
    "isReported",
    "isAggregate",
)


def partner_name(code: Any) -> Optional[str]:
    try:
        return PARTNER_NAMES.get(int(code))
    except (TypeError, ValueError):
        return None


def expand_periods(url: str, years: Any) -> List[str]:
    """One URL per year of ``YEARS`` (``2020,2022`` / ``2015-2024``); the preview API allows a single period per call."""
    text = str(years or "").strip()
    if not text:
        return [url]
    wanted: List[int] = []
    for part in re.split(r"[;,\s]+", text):
        if "-" in part:
            start, end = part.split("-", 1)
            wanted.extend(range(int(start), int(end) + 1))
        elif part.isdigit():
            wanted.append(int(part))
    return [re.sub(r"period=[^&]*", f"period={year}", url) for year in sorted(set(wanted))]


def fetch_preview(http: HttpClient, url: str, timeout: int = 60) -> List[Dict[str, Any]]:
    """GET a preview query; the free tier rate-limits (429) so retry generously."""
    resp = http.get(url, timeout=timeout, max_retries=6, base_sleep=5.0)
    payload = resp.json()
    if not isinstance(payload, dict):
        raise SourceUnavailable(f"Unexpected Comtrade payload for {url}")
    if payload.get("error"):
        raise SourceUnavailable(f"Comtrade error for {url}: {payload['error']}")
    rows = list(payload.get("data") or [])
    match = re.search(r"maxRecords=(\d+)", url)
    if match and len(rows) >= int(match.group(1)):
        logger.warning("Comtrade preview returned maxRecords=%s rows; raise maxRecords in the URL (API max 500)", match.group(1))
    return rows


def to_record(row: Dict[str, Any]) -> Dict[str, Any]:
    out = {key: row.get(key) for key in RECORD_KEYS}
    out["partner_name"] = partner_name(row.get("partnerCode"))
    return out
