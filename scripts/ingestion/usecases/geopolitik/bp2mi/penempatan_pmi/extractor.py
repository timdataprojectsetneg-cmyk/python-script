"""BP2MI Penempatan PMI: "Berdasarkan Negara" table of the monthly Laporan Publikasi PDF.

``URL`` is a direct PDF link or a landing page listing the reports (default:
the BP2MI Jawa Barat statistics page; the newest report of every data year is
read, picked from the date in the file name). ``SOURCE_FILE`` reads a saved copy of the PDF.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator

from .....core.base.extractor import BaseExtractor
from .._laporan import extract_reports

logger = logging.getLogger(__name__)

TITLE = re.compile(
    r"Layanan\s+Penempatan\s+Pekerja\s+Migran\s+Indonesia\s+Tahun\s+(\d{4})[^\n]*\n\s*Berdasarkan\s+Negara\s+Layanan\s+Penempatan",
    re.I,
)


class Extractor(BaseExtractor):
    def extract(self) -> Iterator[Dict[str, Any]]:
        count = 0
        for row in extract_reports(
            self.http, self.config.get("url"), self.config.get("source_file"), TITLE, "bp2mi penempatan_pmi"
        ):
            count += 1
            yield row
        logger.info("BP2MI penempatan_pmi: %d rows", count)
