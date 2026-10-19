"""CSV Extractor for US Treasury OFAC SDN Sanctions List.

Downloads and parses the official Specially Designated Nationals (SDN) CSV:
https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV
Extracts sanctioned corporate entities, financial institutions, vessels, and individuals.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Any, Dict, Iterator
import requests

from .....core.base.extractor import BaseExtractor

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV"
)


class Extractor(BaseExtractor):
    """CSV extractor for US OFAC Specially Designated Nationals list."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_URL)

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Stream and parse OFAC SDN CSV."""
        logger.info("Fetching OFAC SDN list from %s", self.url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/csv, text/plain, */*",
        }

        try:
            resp = requests.get(self.url, headers=headers, timeout=40, stream=True)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("Failed to download OFAC SDN CSV: %s", exc)
            return

        reader = csv.reader(resp.iter_lines(decode_unicode=True))
        count = 0

        for row in reader:
            if not row or len(row) < 4:
                continue

            count += 1
            ent_num = row[0].strip()
            name = row[1].strip()
            sdn_type = row[2].strip()
            program = row[3].strip()
            remarks = row[11].strip() if len(row) > 11 else ""

            yield {
                "ent_num": ent_num,
                "name": name,
                "type": sdn_type,
                "program": program,
                "remarks": remarks,
            }

        logger.info("Extracted %d SDN sanctioned entities from OFAC list", count)
