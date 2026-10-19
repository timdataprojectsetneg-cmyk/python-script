"""API Extractor for GDACS Global Disaster Emergency Alerts.

Parses the official multi-hazard alert RSS feed from GDACS (UN / European Commission):
https://www.gdacs.org/xml/rss.xml
Extracts global earthquakes, tropical cyclones, tsunamis, floods, volcanoes, and wildfires.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List
import xml.etree.ElementTree as ET
import requests

from .....core.base.extractor import BaseExtractor

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.gdacs.org/xml/rss.xml"


class Extractor(BaseExtractor):
    """RSS / XML extractor for GDACS multi-hazard global alerts."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_URL)

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Download GDACS RSS XML and yield disaster event records."""
        logger.info("Fetching GDACS multi-hazard RSS feed from %s", self.url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
        }

        try:
            resp = requests.get(self.url, headers=headers, timeout=30)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
        except Exception as exc:
            logger.error("Failed to fetch or parse GDACS RSS feed: %s", exc)
            return

        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else []
        logger.info("Discovered %d disaster alert items in GDACS feed", len(items))

        for item in items:
            raw_rec: Dict[str, Any] = {}
            for child in item:
                # Strip XML namespace if present
                tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                raw_rec[tag] = child.text

            yield raw_rec
