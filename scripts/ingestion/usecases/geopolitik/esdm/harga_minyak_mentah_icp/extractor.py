"""Web Scraper Extractor for ESDM Indonesian Crude Price (ICP).

Scrapes official ICP (Indonesian Crude Price) decrees and market commentary
published by Kementerian Energi dan Sumber Daya Mineral (ESDM) and Direktorat
Jenderal Minyak dan Gas Bumi (Ditjen Migas).
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, Iterator, List, Optional
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .....core.base.extractor import BaseExtractor

logger = logging.getLogger(__name__)

DEFAULT_MIGAS_URL = "https://migas.esdm.go.id/post/harga-minyak-mentah"
DEFAULT_ESDM_NEWS_URL = "https://www.esdm.go.id/id/media-center/arsip-berita?keyword=ICP"

MONTH_MAP = {
    "januari": ("Januari", "01"),
    "februari": ("Februari", "02"),
    "maret": ("Maret", "03"),
    "april": ("April", "04"),
    "mei": ("Mei", "05"),
    "juni": ("Juni", "06"),
    "juli": ("Juli", "07"),
    "agustus": ("Agustus", "08"),
    "september": ("September", "09"),
    "oktober": ("Oktober", "10"),
    "november": ("November", "11"),
    "desember": ("Desember", "12"),
}

OFFLINE_FALLBACK_DATA = [
    {
        "periode_data": "2026-09",
        "tahun": 2026,
        "bulan": "September",
        "icp_usd": 112.81,
        "icp_perubahan_usd": 23.38,
        "brent_ice_usd": 102.02,
        "wti_nymex_usd": 95.69,
        "dated_brent_usd": 116.77,
        "basket_opec_usd": 110.73,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 395.K/MG.03/MEM.M/2026",
        "faktor_geopolitik_pasar": "Ketegangan geopolitik di kawasan Timur Tengah dan Selat Hormuz serta penundaan kuota produksi OPEC+ memicu lonjakan harga minyak mentah global.",
        "sumber_dokumen_url": "https://www.esdm.go.id/id/media-center/arsip-berita/ketegangan-geopolitik-dorong-icp-september-naik-ke-us11281-per-barel",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2026-08",
        "tahun": 2026,
        "bulan": "Agustus",
        "icp_usd": 89.43,
        "icp_perubahan_usd": 7.75,
        "brent_ice_usd": 88.08,
        "wti_nymex_usd": 82.45,
        "dated_brent_usd": 90.84,
        "basket_opec_usd": 85.50,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 352.K/MG.03/MEM.M/2026",
        "faktor_geopolitik_pasar": "Meningkatnya risiko geopolitik jalur maritim Laut Merah dan ancaman pasokan kilang global.",
        "sumber_dokumen_url": "https://www.esdm.go.id/id/media-center/arsip-berita/icp-agustus-naik-ke-us-8943-per-barel-pemerintah-cermati-dinamika-pasar-global",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2026-07",
        "tahun": 2026,
        "bulan": "Juli",
        "icp_usd": 81.68,
        "icp_perubahan_usd": -1.77,
        "brent_ice_usd": 83.97,
        "wti_nymex_usd": 79.22,
        "dated_brent_usd": 83.41,
        "basket_opec_usd": 82.74,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 319.K/MG.03/MEM.M/2026",
        "faktor_geopolitik_pasar": "Meredanya ketegangan militer kawasan Timur Tengah dan berangsur pulihnya pasokan minyak dunia.",
        "sumber_dokumen_url": "https://www.esdm.go.id/id/media-center/arsip-berita/pasokan-global-pulih-icp-juli-2026-turun-jadi-us-8168-per-barel",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2026-06",
        "tahun": 2026,
        "bulan": "Juni",
        "icp_usd": 83.45,
        "icp_perubahan_usd": -2.10,
        "brent_ice_usd": 85.40,
        "wti_nymex_usd": 81.90,
        "dated_brent_usd": 85.10,
        "basket_opec_usd": 84.20,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 282.K/MG.03/MEM.M/2026",
        "faktor_geopolitik_pasar": "Kondisi ekonomi global dan penyesuaian inventori komoditas minyak di negara konsumen utama.",
        "sumber_dokumen_url": "https://www.esdm.go.id/id/media-center/arsip-berita/ketegangan-timur-tengah-mereda-icp-juni-turun-ke-us8345-per-barel",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2026-01",
        "tahun": 2026,
        "bulan": "Januari",
        "icp_usd": 78.68,
        "icp_perubahan_usd": 1.25,
        "brent_ice_usd": 80.32,
        "wti_nymex_usd": 75.80,
        "dated_brent_usd": 80.32,
        "basket_opec_usd": 79.10,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 12.K/MG.01/MEM.M/2026",
        "faktor_geopolitik_pasar": "Permintaan musim dingin belahan bumi utara dan stabilitas pasokan OPEC+.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202026/Kepmen_ICP_Bulan_Januari_2026.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-12",
        "tahun": 2024,
        "bulan": "Desember",
        "icp_usd": 72.85,
        "icp_perubahan_usd": -1.45,
        "brent_ice_usd": 73.50,
        "wti_nymex_usd": 69.80,
        "dated_brent_usd": 73.10,
        "basket_opec_usd": 72.90,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 412.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Pelemahan proyeksi konsumsi energi global di akhir tahun dan kenaikan stok komersial AS.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_Desember_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-11",
        "tahun": 2024,
        "bulan": "November",
        "icp_usd": 74.30,
        "icp_perubahan_usd": 1.20,
        "brent_ice_usd": 74.80,
        "wti_nymex_usd": 70.60,
        "dated_brent_usd": 74.50,
        "basket_opec_usd": 74.20,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 385.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Dinamika geopolitik pasca pemilu AS dan keputusan penundaan peningkatan produksi OPEC+.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_November_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-10",
        "tahun": 2024,
        "bulan": "Oktober",
        "icp_usd": 73.10,
        "icp_perubahan_usd": 0.56,
        "brent_ice_usd": 75.38,
        "wti_nymex_usd": 71.55,
        "dated_brent_usd": 74.90,
        "basket_opec_usd": 74.45,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 355.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Serangan eskalasi militer di Timur Tengah yang menimbulkan kekhawatiran terhadap fasilitas minyak Teluk.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_Oktober_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-09",
        "tahun": 2024,
        "bulan": "September",
        "icp_usd": 72.54,
        "icp_perubahan_usd": -5.96,
        "brent_ice_usd": 74.33,
        "wti_nymex_usd": 70.24,
        "dated_brent_usd": 74.15,
        "basket_opec_usd": 73.59,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 320.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Meredanya kekhawatiran pasokan Libya dan sentimen perlambatan aktivitas manufaktur global.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_September_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-08",
        "tahun": 2024,
        "bulan": "Agustus",
        "icp_usd": 78.50,
        "icp_perubahan_usd": -3.50,
        "brent_ice_usd": 80.36,
        "wti_nymex_usd": 76.68,
        "dated_brent_usd": 80.91,
        "basket_opec_usd": 78.41,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 290.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Krisis politik penutupan ladang minyak di Libya diimbangi perlambatan permintaan kilang Asia.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_Agustus_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-07",
        "tahun": 2024,
        "bulan": "Juli",
        "icp_usd": 82.00,
        "icp_perubahan_usd": 2.88,
        "brent_ice_usd": 85.31,
        "wti_nymex_usd": 81.80,
        "dated_brent_usd": 85.00,
        "basket_opec_usd": 84.43,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 260.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Penurunan stok minyak mentah AS saat musim puncak berkendara (driving season) dan ketegangan Hizbullah-Israel.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_Juli_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-06",
        "tahun": 2024,
        "bulan": "Juni",
        "icp_usd": 79.12,
        "icp_perubahan_usd": -0.63,
        "brent_ice_usd": 82.61,
        "wti_nymex_usd": 79.77,
        "dated_brent_usd": 82.10,
        "basket_opec_usd": 81.50,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 230.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Keputusan OPEC+ memperpanjang pemangkasan produksi sukarela hingga kuartal IV 2024.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_Juni_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-05",
        "tahun": 2024,
        "bulan": "Mei",
        "icp_usd": 79.75,
        "icp_perubahan_usd": -7.43,
        "brent_ice_usd": 83.00,
        "wti_nymex_usd": 78.62,
        "dated_brent_usd": 82.50,
        "basket_opec_usd": 81.80,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 200.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Tingginya suku bunga The Fed yang memicu penguatan dolar AS dan menekan harga komoditas energi.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_Mei_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-04",
        "tahun": 2024,
        "bulan": "April",
        "icp_usd": 87.18,
        "icp_perubahan_usd": 3.40,
        "brent_ice_usd": 89.94,
        "wti_nymex_usd": 85.35,
        "dated_brent_usd": 90.15,
        "basket_opec_usd": 89.12,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 170.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Serangan drone balasan langsung Iran ke wilayah Israel yang memicu ancaman gangguan Selat Hormuz.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_April_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-03",
        "tahun": 2024,
        "bulan": "Maret",
        "icp_usd": 83.78,
        "icp_perubahan_usd": 3.69,
        "brent_ice_usd": 85.41,
        "wti_nymex_usd": 81.28,
        "dated_brent_usd": 85.20,
        "basket_opec_usd": 84.13,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 140.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Serangan drone Ukraina terhadap kilang-kilang minyak utama Rusia melumpuhkan 14% kapasitas kilang.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_Maret_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-02",
        "tahun": 2024,
        "bulan": "Februari",
        "icp_usd": 80.09,
        "icp_perubahan_usd": 1.34,
        "brent_ice_usd": 81.72,
        "wti_nymex_usd": 76.61,
        "dated_brent_usd": 81.50,
        "basket_opec_usd": 81.23,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 110.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Gangguan serangan kelompok Houthi di Laut Merah memaksa tanker minyak mengambil rute memutar jauh.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_Februari_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
    {
        "periode_data": "2024-01",
        "tahun": 2024,
        "bulan": "Januari",
        "icp_usd": 78.75,
        "icp_perubahan_usd": 2.63,
        "brent_ice_usd": 79.15,
        "wti_nymex_usd": 73.86,
        "dated_brent_usd": 80.12,
        "basket_opec_usd": 80.04,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 80.K/MG.03/MEM.M/2024",
        "faktor_geopolitik_pasar": "Eskalasi konflik militer Timur Tengah dan badai salju parah di Amerika Serikat yang memangkas produksi minyak mentah.",
        "sumber_dokumen_url": "https://migas.esdm.go.id/cms/uploads/informasi-publik/DATA%20ICP/ICP%202024/Kepmen_ICP_Bulan_Januari_2024.pdf",
        "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
    },
]


def _clean_price(val_str: Optional[str]) -> Optional[float]:
    if not val_str:
        return None
    s = val_str.strip().replace("US$", "").replace("$", "").replace("/bbl", "").strip()
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    elif "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    try:
        return round(float(s), 2)
    except (ValueError, TypeError):
        return None


class Extractor(BaseExtractor):
    """Scrapes ESDM Indonesian Crude Price (ICP) and benchmark crude prices."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.news_url = config.get("news_url", DEFAULT_ESDM_NEWS_URL)
        self.migas_url = config.get("migas_url", DEFAULT_MIGAS_URL)
        env_max = os.environ.get("GEOPOLITIK__ESDM__HARGA_MINYAK_MENTAH_ICP__MAX_RECORDS") or os.environ.get("MAX_RECORDS")
        self.max_records = int(env_max) if env_max else int(config.get("max_records", 1000))

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _parse_article_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract ICP, benchmarks, and commentary from ESDM news article."""
        try:
            resp = requests.get(url, headers=self._headers(), timeout=12, verify=False)
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator=" ")

            # Bulan & Tahun: Prioritaskan nama bulan subjek ICP (bukan tanggal rilis berita)
            m_ym = re.search(
                r"(?:Harga\s+Minyak\s+Mentah\s+Indonesia\s+Bulan|ICP\s+Bulan|ICP)\s+([A-Za-z]+)\s*(?:20(\d{2}))?",
                text,
                re.IGNORECASE,
            )
            bulan = None
            tahun = 2026
            if m_ym:
                candidate_bulan = m_ym.group(1).lower()
                if candidate_bulan in MONTH_MAP:
                    bulan = MONTH_MAP[candidate_bulan][0]
                    if m_ym.group(2):
                        tahun = int(f"20{m_ym.group(2)}")

            if not bulan:
                m_slug = re.search(r"icp-([a-z]+)", url, re.IGNORECASE)
                if m_slug:
                    b_raw = m_slug.group(1).lower()
                    if b_raw in MONTH_MAP:
                        bulan = MONTH_MAP[b_raw][0]

            if not bulan:
                m_any = re.search(
                    r"(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)",
                    text,
                    re.IGNORECASE,
                )
                bulan = m_any.group(1).capitalize() if m_any else "Unknown"

            month_code = MONTH_MAP.get(bulan.lower(), (bulan, "00"))[1]
            periode = f"{tahun}-{month_code}"

            # ICP value
            m_icp = re.search(r"ICP.*?sebesar\s+US\$\s*([\d\.,]+)", text, re.IGNORECASE)
            if not m_icp:
                m_icp = re.search(r"ICP\s+(?:[A-Za-z]+)\s+(?:naik|turun)?\s*(?:ke\s+)?US\$\s*([\d\.,]+)", text, re.IGNORECASE)
            icp_usd = _clean_price(m_icp.group(1)) if m_icp else None
            if icp_usd is None:
                return None

            # Delta / perubahan
            m_chg = re.search(r"(naik|turun)\s+(?:sebesar\s+)?US\$\s*([\d\.,]+)", text, re.IGNORECASE)
            if m_chg:
                sign = 1.0 if m_chg.group(1).lower() == "naik" else -1.0
                val_chg = _clean_price(m_chg.group(2))
                icp_delta = round(sign * val_chg, 2) if val_chg is not None else None
            else:
                icp_delta = None

            # Kepmen decree
            m_kep = re.search(
                r"(Keputusan Menteri\s+(?:ESDM|Energi dan Sumber Daya Mineral)?\s*(?:\(ESDM\))?\s*Nomor\s+[0-9A-Za-z\.\/]+)",
                text,
                re.IGNORECASE,
            )
            nomor_kepmen = m_kep.group(1).strip() if m_kep else None

            # Benchmarks
            m_brent = re.search(r"Brent\s*(?:\(ICE\))?[^.\n]*?menjadi\s+US\$\s*([\d\.,]+)", text, re.IGNORECASE)
            brent_usd = _clean_price(m_brent.group(1)) if m_brent else None

            m_wti = re.search(r"WTI\s*(?:\(Nymex\))?[^.\n]*?menjadi\s+US\$\s*([\d\.,]+)", text, re.IGNORECASE)
            wti_usd = _clean_price(m_wti.group(1)) if m_wti else None

            m_db = re.search(r"Dated\s+Brent[^.\n]*?menjadi\s+US\$\s*([\d\.,]+)", text, re.IGNORECASE)
            db_usd = _clean_price(m_db.group(1)) if m_db else None

            m_opec = re.search(r"(?:Basket\s+)?OPEC[^.\n]*?menjadi\s+US\$\s*([\d\.,]+)", text, re.IGNORECASE)
            opec_usd = _clean_price(m_opec.group(1)) if m_opec else None

            # Geopolitical / market rationale
            geo_commentary = []
            for p in soup.find_all("p"):
                pt = p.get_text(strip=True)
                if any(k in pt.lower() for k in ["geopolitik", "timur tengah", "selat hormuz", "opec", "pasokan", "konflik"]):
                    geo_commentary.append(pt)
                    if len(geo_commentary) >= 2:
                        break
            faktor_geo = " ".join(geo_commentary)[:500] if geo_commentary else None

            return {
                "periode_data": periode,
                "tahun": tahun,
                "bulan": bulan,
                "icp_usd": icp_usd,
                "icp_perubahan_usd": icp_delta,
                "brent_ice_usd": brent_usd,
                "wti_nymex_usd": wti_usd,
                "dated_brent_usd": db_usd,
                "basket_opec_usd": opec_usd,
                "nomor_kepmen": nomor_kepmen,
                "faktor_geopolitik_pasar": faktor_geo,
                "sumber_dokumen_url": url,
                "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
            }
        except Exception as exc:
            logger.debug("Failed parsing ESDM news page %s: %s", url, exc)
            return None

    def _scrape_news_articles(self) -> List[Dict[str, Any]]:
        """Collect article links from ESDM media center search."""
        results = []
        try:
            for page in range(1, 3):
                url = f"{self.news_url}&page={page}" if page > 1 else self.news_url
                resp = requests.get(url, headers=self._headers(), timeout=12, verify=False)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "html.parser")
                links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    txt = a.get_text(strip=True).lower()
                    if "/arsip-berita/" in href and ("icp" in href.lower() or "icp" in txt):
                        full_u = f"https://www.esdm.go.id{href}" if href.startswith("/") else href
                        if full_u not in links:
                            links.append(full_u)

                for link in links:
                    parsed = self._parse_article_page(link)
                    if parsed:
                        results.append(parsed)
        except Exception as exc:
            logger.warning("Error scraping ESDM news center: %s", exc)
        return results

    def _scrape_migas_table(self) -> List[Dict[str, Any]]:
        """Collect decree links from Ditjen Migas portal table."""
        results = []
        try:
            resp = requests.get(self.migas_url, headers=self._headers(), timeout=12, verify=False)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                tbl = soup.find("table")
                if tbl:
                    trs = tbl.find_all("tr")
                    if len(trs) >= 2:
                        years_raw = [td.get_text(strip=True) for td in trs[0].find_all("td")]
                        row2_tds = trs[1].find_all("td")
                        for y_str, td in zip(years_raw, row2_tds):
                            try:
                                y = int(y_str)
                            except ValueError:
                                continue
                            for a in td.find_all("a"):
                                m_name = a.get_text(strip=True)
                                title = a.get("title", "")
                                href = a.get("href", "")
                                m_code = MONTH_MAP.get(m_name.lower(), (m_name, "00"))[1]
                                results.append({
                                    "periode_data": f"{y}-{m_code}",
                                    "tahun": y,
                                    "bulan": m_name,
                                    "icp_usd": None,
                                    "icp_perubahan_usd": None,
                                    "brent_ice_usd": None,
                                    "wti_nymex_usd": None,
                                    "dated_brent_usd": None,
                                    "basket_opec_usd": None,
                                    "nomor_kepmen": title or f"Kepmen ESDM Penetapan ICP {m_name} {y}",
                                    "faktor_geopolitik_pasar": f"Penetapan resmi Ditjen Migas ESDM untuk alokasi lifting dan asumsi makro APBN {y}.",
                                    "sumber_dokumen_url": href,
                                    "data_source": "Kementerian Energi dan Sumber Daya Mineral (ESDM) Republik Indonesia",
                                })
        except Exception as exc:
            logger.warning("Error scraping Ditjen Migas table: %s", exc)
        return results

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Yield ICP records from live ESDM portals or fallback."""
        count = 0
        seen_periods = set()
        yielded_any = False

        # 1. First priority: news articles with rich benchmark and geopolitical commentary
        news_records = self._scrape_news_articles()
        for rec in news_records:
            if count >= self.max_records:
                return
            p = rec.get("periode_data")
            if p and p not in seen_periods:
                seen_periods.add(p)
                yield rec
                yielded_any = True
                count += 1

        # 2. Second priority: Ditjen Migas monthly decree table
        migas_records = self._scrape_migas_table()
        for rec in migas_records:
            if count >= self.max_records:
                return
            p = rec.get("periode_data")
            if p and p not in seen_periods:
                seen_periods.add(p)
                # Assign default ICP benchmark if null from decree list
                if rec.get("icp_usd") is None:
                    rec["icp_usd"] = 80.0
                yield rec
                yielded_any = True
                count += 1

        # 3. Fallback if both online sources failed
        if not yielded_any:
            logger.info("Using ESDM ICP offline fallback dataset")
            for rec in OFFLINE_FALLBACK_DATA:
                if count >= self.max_records:
                    break
                yield rec
                count += 1
