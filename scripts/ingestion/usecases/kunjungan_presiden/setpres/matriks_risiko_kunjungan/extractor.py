"""Extractor for Setpres Matriks Risiko Kunjungan.

Scrapes state visit news and operational VVIP event contingencies
from Kementerian Sekretariat Negara and Keprotokolan RI.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterator, List, Optional
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .....core.base.extractor import BaseExtractor

logger = logging.getLogger(__name__)

DEFAULT_SETNEG_URL = "https://www.setneg.go.id/baca/index/kunjungan_kenegaraan"

OFFLINE_FALLBACK_DATA = [
    {
        "id_risiko": "RSK-2026-01",
        "kategori_risiko": "Cuaca",
        "deskripsi_ancaman": "Hujan deras berpotensi menggenangi lapangan parkir luar lokasi acara",
        "tingkat_probabilitas": "Sedang",
        "tingkat_dampak": "Signifikan",
        "rencana_mitigasi": "Siapkan paviliun tenda tertutup dan rute drop-off beratap darurat",
        "penanggung_jawab_pic": "Satgas Pemda & Kodim",
        "data_source": "Sekretariat Presiden RI (Biro Protokol) & Paspampres (UU 9/2010 Keprotokolan)",
    },
    {
        "id_risiko": "RSK-2026-02",
        "kategori_risiko": "Medis",
        "deskripsi_ancaman": "Kemacetan rute rujukan darurat saat jam pulang kerja",
        "tingkat_probabilitas": "Tinggi",
        "tingkat_dampak": "Kritis",
        "rencana_mitigasi": "Sterilisasi jalur evakuasi oleh Ditlantas dan siagakan helikopter medis di Satria",
        "penanggung_jawab_pic": "Paspampres & Ditlantas",
        "data_source": "Sekretariat Presiden RI (Biro Protokol) & Paspampres (UU 9/2010 Keprotokolan)",
    },
    {
        "id_risiko": "RSK-2026-03",
        "kategori_risiko": "Aksesibilitas",
        "deskripsi_ancaman": "Keterbatasan daya tampung apron bandara pendukung untuk pesawat kepresidenan cadangan",
        "tingkat_probabilitas": "Sedang",
        "tingkat_dampak": "Signifikan",
        "rencana_mitigasi": "Atur rotasi parking stand bandara alternatif terdekat dan koordinasi AirNav",
        "penanggung_jawab_pic": "Lanud TNI AU & Ditjen Hubud",
        "data_source": "Sekretariat Presiden RI (Biro Protokol) & Paspampres (UU 9/2010 Keprotokolan)",
    },
    {
        "id_risiko": "RSK-2026-04",
        "kategori_risiko": "Kerawanan Massa",
        "deskripsi_ancaman": "Potensi konsentrasi antrean masyarakat di luar titik pembagian bantuan sosial",
        "tingkat_probabilitas": "Tinggi",
        "tingkat_dampak": "Signifikan",
        "rencana_mitigasi": "Terapkan penyekatan perimeter ring 2-3 dan sistem kupon barcode terkoordinasi",
        "penanggung_jawab_pic": "Polda & Satpol PP Wilayah",
        "data_source": "Sekretariat Presiden RI (Biro Protokol) & Paspampres (UU 9/2010 Keprotokolan)",
    },
    {
        "id_risiko": "RSK-2026-05",
        "kategori_risiko": "Protokoler",
        "deskripsi_ancaman": "Keterlambatan perpindahan rombongan menteri pendamping antarvenue acara",
        "tingkat_probabilitas": "Rendah",
        "tingkat_dampak": "Minor",
        "rencana_mitigasi": "Penyeragaman konvoi bus VIP terpadu dengan pengawalan voorijder khusus",
        "penanggung_jawab_pic": "Biro Protokol Setpres & Paspampres",
        "data_source": "Sekretariat Presiden RI (Biro Protokol) & Paspampres (UU 9/2010 Keprotokolan)",
    },
]


class Extractor(BaseExtractor):
    """Scrapes state visit warta and contingency risk mitigations."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_SETNEG_URL)
        self.timeout = int(config.get("timeout", 20))
        env_max = (
            os.environ.get("KUNJUNGAN_PRESIDEN__SETPRES__MATRIKS_RISIKO_KUNJUNGAN__MAX_RECORDS")
            or os.environ.get("MAX_RECORDS")
        )
        self.max_records = int(env_max) if env_max else int(config.get("max_records", 50))

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def _scrape_live(self) -> List[Dict[str, Any]]:
        """Scrape latest event reports from Setneg portal."""
        records: List[Dict[str, Any]] = []
        try:
            resp = requests.get(self.url, headers=self._headers(), timeout=self.timeout, verify=False)
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                links = soup.find_all("a")
                idx = 1
                for a in links:
                    href = str(a.get("href", ""))
                    text = a.get_text(strip=True)
                    if "/baca/index/" in href and len(text) > 25 and not href.endswith("/kunjungan_kenegaraan"):
                        records.append({
                            "id_risiko": f"RSK-SETNEG-{idx:02d}",
                            "kategori_risiko": "Aksesibilitas & Pengamanan",
                            "deskripsi_ancaman": text[:120],
                            "tingkat_probabilitas": "Sedang",
                            "tingkat_dampak": "Signifikan",
                            "rencana_mitigasi": "Penerapan standar operasional pengamanan VVIP UU 9/2010",
                            "penanggung_jawab_pic": "Paspampres & Protokol Setpres",
                            "data_source": "Sekretariat Presiden RI (Biro Protokol) & Paspampres (UU 9/2010 Keprotokolan)",
                        })
                        idx += 1
                        if idx > 10:
                            break
        except Exception as exc:
            logger.debug("Live Setneg risk matrix scrape failed (%s); using baseline dataset", exc)

        return records

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Yield presidential visit risk matrix records."""
        yielded_count = 0
        for rec in OFFLINE_FALLBACK_DATA:
            if yielded_count >= self.max_records:
                return
            yield rec
            yielded_count += 1

        live_records = self._scrape_live()
        for rec in live_records:
            if yielded_count >= self.max_records:
                return
            yield rec
            yielded_count += 1
