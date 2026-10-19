"""Web Scraper Extractor for Kemenkes SIRANAP Referral Hospital Facilities.

Scrapes live hospital bed availability from the official Kemenkes SIRANAP portal:
https://keslan.kemkes.go.id/app/siranap/rumah_sakit
Extracts hospital registration codes, facility names, address, empty bed counts,
and ICU/VVIP capacities.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator, List
from bs4 import BeautifulSoup

from .....core.base.extractor import BaseExtractor

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://keslan.kemkes.go.id/app/siranap/rumah_sakit"


class Extractor(BaseExtractor):
    """HTML scraper extractor for Kemenkes SIRANAP portal."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_URL)
        self.jenis = str(config.get("jenis", "2"))
        self.propinsi = str(config.get("propinsi", "31prop"))
        self.kabkota = str(config.get("kabkota", "3171"))

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Fetch and scrape SIRANAP hospital cards."""
        import requests

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://keslan.kemkes.go.id/app/siranap/",
        }
        params = {
            "jenis": self.jenis,
            "propinsi": self.propinsi,
            "kabkota": self.kabkota,
        }

        logger.info("Scraping SIRANAP from %s with params %s", self.url, params)
        try:
            resp = requests.get(self.url, params=params, headers=headers, timeout=25)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("Failed to fetch SIRANAP portal: %s", exc)
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="cardRS")
        logger.info("Discovered %d hospital cards on SIRANAP portal", len(cards))

        for card in cards:
            h5 = card.find("h5")
            nama_rs = h5.text.strip() if h5 else "RS"
            p = card.find("p")
            alamat = p.text.strip() if p else ""

            # Extract registration code from detail link
            link_detail = card.find("a", href=re.compile(r"kode_rs="))
            kode_rs = ""
            if link_detail:
                m = re.search(r"kode_rs=(\d+)", link_detail.get("href", ""))
                if m:
                    kode_rs = m.group(1)

            # Analyze room and bed occupancy rows
            rows = card.find_all("tr")
            total_kosong = 0
            icu_vvip_kosong = 0
            total_ruang = 0

            for row in rows:
                tds = [td.text.strip() for td in row.find_all("td")]
                if len(tds) >= 3:
                    total_ruang += 1
                    kelas_kamar = tds[0]
                    nama_ruang = tds[1]
                    bed_str = tds[2]

                    m_bed = re.search(r"Tersedia\s+(\d+)", bed_str, re.IGNORECASE)
                    avail = int(m_bed.group(1)) if m_bed else 0
                    total_kosong += avail

                    if any(k in f"{kelas_kamar} {nama_ruang}".upper() for k in ["ICU", "ICCU", "VVIP", "VIP", "HCU"]):
                        icu_vvip_kosong += avail

            yield {
                "kode_rs": kode_rs if kode_rs else f"RS-{abs(hash(nama_rs)) % 10000000}",
                "nama_rs": nama_rs,
                "alamat_rs": alamat,
                "total_bed_kosong": total_kosong,
                "bed_icu_vvip_kosong": icu_vvip_kosong,
                "total_ruangan": total_ruang,
                "provinsi": "DKI Jakarta",
                "kabupaten_kota": "Jakarta Selatan",
            }
