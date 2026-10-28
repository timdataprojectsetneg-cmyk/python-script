"""BMKG felt earthquakes (gempadirasakan.xml, ~15 latest events).

data.bmkg.go.id answers 403 to plain HTTP clients, so ``impersonate`` defaults
to ``chrome`` (curl_cffi).
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator, List, Optional

from .....core.base.extractor import BaseExtractor
from .....exceptions import SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.xml"
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def _float(text: Optional[str]) -> Optional[float]:
    match = _NUMBER.search(text or "")
    return float(match.group()) if match else None


def parse_xml(content: bytes) -> List[Dict[str, Any]]:
    """Parse the ``<Infogempa>`` document into dictionary-named records."""
    from lxml import etree

    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    try:
        root = etree.fromstring(content, parser)
    except etree.XMLSyntaxError as exc:
        raise SourceUnavailable(f"BMKG returned invalid XML: {exc}") from exc

    rows: List[Dict[str, Any]] = []
    for node in root.iter("gempa"):
        def text(tag: str) -> Optional[str]:
            child = node.find(tag)
            return (child.text or "").strip() if child is not None and child.text else None

        coords = text("point/coordinates")
        latitude = longitude = None
        if coords and "," in coords:
            lat_text, lon_text = coords.split(",", 1)
            latitude, longitude = _float(lat_text), _float(lon_text)
        kedalaman = text("Kedalaman")
        rows.append(
            {
                "tanggal": text("Tanggal"),
                "jam": text("Jam"),
                "datetime": text("DateTime"),
                "point_coordinates": coords,
                "lintang": text("Lintang"),
                "bujur": text("Bujur"),
                "magnitude": _float(text("Magnitude")),
                "kedalaman": kedalaman,
                "wilayah": text("Wilayah"),
                "dirasakan": text("Dirasakan"),
                "latitude": latitude,
                "longitude": longitude,
                "kedalaman_km": _float(kedalaman),
            }
        )
    return rows


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        if not merged.get("impersonate"):
            merged["impersonate"] = "chrome"
        super().__init__(merged)

    def extract(self) -> Iterator[Dict[str, Any]]:
        url = self.config.get("url") or DEFAULT_URL
        resp = self.http.get(url, timeout=60)
        rows = parse_xml(resp.content)
        if not rows:
            raise SourceUnavailable(f"BMKG feed at {url} contained no <gempa> entries")
        yield from rows
