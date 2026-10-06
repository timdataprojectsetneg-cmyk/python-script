"""Shared extractor base for the BPS WebAPI ``list/model/data`` endpoints.

BPS returns one payload per request with a flat ``datacontent`` map keyed by a
concatenated id ``{vervar}{var}{turvar}{tahun}{turtahun}``. This base turns that
into one row per entity (province / city), one column per month (+ optional
extra periods such as ``tahunan``).

Subclasses set ``ENTITY_FIELD`` and (optionally) ``EXTRA_TURTAHUN_FIELDS``::

    class Extractor(BpsWebApiExtractor):
        ENTITY_FIELD = "provinsi"
        PREFER_TURVAR = True
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, Iterator, List, Optional

from ....config import get_raw
from ....core.base.extractor import BaseExtractor
from ....exceptions import SourceUnavailable

logger = logging.getLogger(__name__)

TH_RE = re.compile(r"/th/(\d+)")

# BPS month labels (English or Indonesian) -> canonical field name.
MONTH_FIELDS = {
    "january": "januari", "february": "februari", "march": "maret", "april": "april",
    "may": "mei", "june": "juni", "july": "juli", "august": "agustus",
    "september": "september", "october": "oktober", "november": "november",
    "december": "desember",
    "januari": "januari", "februari": "februari", "maret": "maret", "mei": "mei",
    "juni": "juni", "juli": "juli", "agustus": "agustus", "oktober": "oktober",
    "nopember": "november", "desember": "desember",
}
MONTH_ORDER = [
    "januari", "februari", "maret", "april", "mei", "juni",
    "juli", "agustus", "september", "oktober", "november", "desember",
]
TURVAR_PREFERRED = ("general", "umum", "total", "all")


def to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    if text in ("", "-", ".."):
        return None
    try:
        return float(text)
    except ValueError:
        return None


class BpsWebApiExtractor(BaseExtractor):
    ENTITY_FIELD = "provinsi"
    PREFER_TURVAR = False
    EXTRA_TURTAHUN_FIELDS: Dict[str, str] = {}
    RETRIES = 3

    def _fields(self) -> List[str]:
        extras = list(dict.fromkeys(self.EXTRA_TURTAHUN_FIELDS.values()))
        return [self.ENTITY_FIELD] + MONTH_ORDER + extras + ["tahun"]

    def _turtahun_fields(self) -> Dict[str, str]:
        return {**MONTH_FIELDS, **self.EXTRA_TURTAHUN_FIELDS}

    def _api_key(self) -> str:
        return (
            self.config.get("api_key")
            or get_raw("BPS_WEBAPI_KEY")
            or get_raw("BPS_API_KEY")
            or ""
        ).strip()

    @staticmethod
    def _with_key(url: str, key: str) -> str:
        return url.replace("WebAPI_KEY", key) if "WebAPI_KEY" in url else url

    def _target_years(self) -> List[int]:
        raw = self.config.get("years")
        if raw:
            return [int(tok) for tok in re.split(r"[,;\s]+", str(raw)) if tok.strip().isdigit()]
        match = TH_RE.search(self.url or "")
        return [int(match.group(1)) + 1900] if match else []

    def _fetch(self, url: str) -> Dict[str, Any]:
        last: Optional[Exception] = None
        for attempt in range(1, self.RETRIES + 1):
            try:
                return self.http.get(url, timeout=60).json()
            except (SourceUnavailable, ValueError) as exc:
                last = exc
                time.sleep(2 * attempt)
        raise SourceUnavailable(f"BPS request failed for {url}: {last}")

    def _turvar_id(self, turvars: List[Dict[str, Any]]) -> str:
        if not turvars:
            return "0"
        if self.PREFER_TURVAR:
            for turvar in turvars:
                label = str(turvar["label"]).strip().lower()
                if any(pref in label for pref in TURVAR_PREFERRED):
                    return str(turvar["val"])
        return str(turvars[0]["val"])

    @staticmethod
    def _tahun_id(tahun_list: List[Dict[str, Any]], year: int) -> str:
        for tahun in tahun_list:
            if str(tahun["label"]) == str(year):
                return str(tahun["val"])
        return str(tahun_list[0]["val"])

    def _rows_from(self, payload: Dict[str, Any], year: int) -> List[Dict[str, Any]]:
        if payload.get("status") != "OK" or payload.get("data-availability") != "available":
            logger.warning(
                "BPS %s: data tidak tersedia (%s / %s)",
                year, payload.get("status"), payload.get("data-availability"),
            )
            return []

        var_id = str(payload["var"][0]["val"])
        turvar_id = self._turvar_id(payload.get("turvar") or [])
        tahun_id = self._tahun_id(payload["tahun"], year)
        fields = self._turtahun_fields()

        mapping: Dict[str, str] = {}
        for turtahun in payload["turtahun"]:
            field = fields.get(str(turtahun["label"]).strip().lower())
            if field:
                mapping[str(turtahun["val"])] = field

        datacontent = payload["datacontent"]
        rows: List[Dict[str, Any]] = []
        for entity in payload["vervar"]:
            entity_id = str(entity["val"])
            row: Dict[str, Any] = {field: None for field in self._fields()}
            row[self.ENTITY_FIELD] = str(entity["label"]).strip()
            row["tahun"] = year
            for turtahun_id, field in mapping.items():
                key = f"{entity_id}{var_id}{turvar_id}{tahun_id}{turtahun_id}"
                row[field] = to_float(datacontent.get(key))
            rows.append(row)
        return rows

    @staticmethod
    def _year_from_payload(payload: Dict[str, Any]) -> Optional[int]:
        tahun_list = payload.get("tahun") or []
        if not tahun_list:
            return None
        label = str(tahun_list[0].get("label", "")).strip()
        return int(label) if label.isdigit() else None

    def extract(self) -> Iterator[Dict[str, Any]]:
        key = self._api_key()
        years = self._target_years()
        if years:
            for year in years:
                url = re.sub(r"/th/\d+", f"/th/{year - 1900}", self.url or "")
                payload = self._fetch(self._with_key(url, key))
                yield from self._rows_from(payload, year)
            return
        payload = self._fetch(self._with_key(self.url, key))
        yield from self._rows_from(payload, self._year_from_payload(payload))
