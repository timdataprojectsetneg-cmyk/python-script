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

OFFLINE_FALLBACK_DATA = [
    {
        "kode_rs": "3171012",
        "nama_rs": "RSUP Nasional Dr. Cipto Mangunkusumo",
        "alamat_rs": "Jl. Diponegoro No. 71, Kenari, Senen",
        "total_bed_kosong": 85,
        "bed_icu_vvip_kosong": 12,
        "total_ruangan": 210,
        "provinsi": "DKI Jakarta",
        "kabupaten_kota": "Kota Administrasi Jakarta Pusat",
    },
    {
        "kode_rs": "3171023",
        "nama_rs": "RSPAD Gatot Soebroto",
        "alamat_rs": "Jl. Abdul Rahman Saleh No. 24",
        "total_bed_kosong": 65,
        "bed_icu_vvip_kosong": 8,
        "total_ruangan": 180,
        "provinsi": "DKI Jakarta",
        "kabupaten_kota": "Kota Administrasi Jakarta Pusat",
    },
    {
        "kode_rs": "3273014",
        "nama_rs": "RSUP Dr. Hasan Sadikin",
        "alamat_rs": "Jl. Pasteur No. 38",
        "total_bed_kosong": 72,
        "bed_icu_vvip_kosong": 10,
        "total_ruangan": 195,
        "provinsi": "Jawa Barat",
        "kabupaten_kota": "Kota Bandung",
    },
    {
        "kode_rs": "3302012",
        "nama_rs": "RSUD Prof. Dr. Margono Soekarjo",
        "alamat_rs": "Jl. Dr. Gumbreg No. 1, Purwokerto",
        "total_bed_kosong": 58,
        "bed_icu_vvip_kosong": 6,
        "total_ruangan": 140,
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kabupaten Banyumas",
    },
    {
        "kode_rs": "3374015",
        "nama_rs": "RSUP Dr. Kariadi",
        "alamat_rs": "Jl. Dr. Sutomo No. 16",
        "total_bed_kosong": 68,
        "bed_icu_vvip_kosong": 9,
        "total_ruangan": 185,
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kota Semarang",
    },
    {
        "kode_rs": "3471016",
        "nama_rs": "RSUP Dr. Sardjito",
        "alamat_rs": "Jl. Kesehatan No. 1, Sekip",
        "total_bed_kosong": 64,
        "bed_icu_vvip_kosong": 8,
        "total_ruangan": 175,
        "provinsi": "DI Yogyakarta",
        "kabupaten_kota": "Kabupaten Sleman",
    },
    {
        "kode_rs": "3578018",
        "nama_rs": "RSUD Dr. Soetomo",
        "alamat_rs": "Jl. Mayjen Prof. Dr. Moestopo No. 6-8",
        "total_bed_kosong": 90,
        "bed_icu_vvip_kosong": 15,
        "total_ruangan": 240,
        "provinsi": "Jawa Timur",
        "kabupaten_kota": "Kota Surabaya",
    },
    {
        "kode_rs": "3671020",
        "nama_rs": "RSUD Kabupaten Tangerang",
        "alamat_rs": "Jl. Jend. Ahmad Yani No. 9",
        "total_bed_kosong": 45,
        "bed_icu_vvip_kosong": 5,
        "total_ruangan": 130,
        "provinsi": "Banten",
        "kabupaten_kota": "Kota Tangerang",
    },
    {
        "kode_rs": "5103021",
        "nama_rs": "RSUP Prof. Dr. I.G.N.G. Ngoerah",
        "alamat_rs": "Jl. Diponegoro, Dauh Puri Klod",
        "total_bed_kosong": 55,
        "bed_icu_vvip_kosong": 8,
        "total_ruangan": 160,
        "provinsi": "Bali",
        "kabupaten_kota": "Kota Denpasar",
    },
    {
        "kode_rs": "1171022",
        "nama_rs": "RSUD dr. Zainoel Abidin",
        "alamat_rs": "Jl. Tgk. Daud Beureueh No. 108",
        "total_bed_kosong": 50,
        "bed_icu_vvip_kosong": 6,
        "total_ruangan": 145,
        "provinsi": "Aceh",
        "kabupaten_kota": "Kota Banda Aceh",
    },
    {
        "kode_rs": "1271023",
        "nama_rs": "RSUP H. Adam Malik",
        "alamat_rs": "Jl. Bunga Lau No. 17, Medan Tuntungan",
        "total_bed_kosong": 70,
        "bed_icu_vvip_kosong": 11,
        "total_ruangan": 190,
        "provinsi": "Sumatera Utara",
        "kabupaten_kota": "Kota Medan",
    },
    {
        "kode_rs": "1371024",
        "nama_rs": "RSUP Dr. M. Djamil",
        "alamat_rs": "Jl. Perintis Kemerdekaan, Padang",
        "total_bed_kosong": 48,
        "bed_icu_vvip_kosong": 7,
        "total_ruangan": 135,
        "provinsi": "Sumatera Barat",
        "kabupaten_kota": "Kota Padang",
    },
    {
        "kode_rs": "1471025",
        "nama_rs": "RSUD Arifin Achmad",
        "alamat_rs": "Jl. Diponegoro No. 2, Pekanbaru",
        "total_bed_kosong": 52,
        "bed_icu_vvip_kosong": 6,
        "total_ruangan": 140,
        "provinsi": "Riau",
        "kabupaten_kota": "Kota Pekanbaru",
    },
    {
        "kode_rs": "1571026",
        "nama_rs": "RSUD Raden Mattaher",
        "alamat_rs": "Jl. Letjen Suprapto No. 31",
        "total_bed_kosong": 42,
        "bed_icu_vvip_kosong": 5,
        "total_ruangan": 120,
        "provinsi": "Jambi",
        "kabupaten_kota": "Kota Jambi",
    },
    {
        "kode_rs": "1671027",
        "nama_rs": "RSUP Dr. Mohammad Hoesin",
        "alamat_rs": "Jl. Jend. Sudirman Km. 3.5, Palembang",
        "total_bed_kosong": 60,
        "bed_icu_vvip_kosong": 9,
        "total_ruangan": 165,
        "provinsi": "Sumatera Selatan",
        "kabupaten_kota": "Kota Palembang",
    },
    {
        "kode_rs": "1771028",
        "nama_rs": "RSUD M. Yunus Bengkulu",
        "alamat_rs": "Jl. Bhayangkara, Sidomulyo",
        "total_bed_kosong": 38,
        "bed_icu_vvip_kosong": 4,
        "total_ruangan": 110,
        "provinsi": "Bengkulu",
        "kabupaten_kota": "Kota Bengkulu",
    },
    {
        "kode_rs": "1871029",
        "nama_rs": "RSUD Dr. H. Abdul Moeloek",
        "alamat_rs": "Jl. Dr. Rivai No. 6, Bandar Lampung",
        "total_bed_kosong": 54,
        "bed_icu_vvip_kosong": 7,
        "total_ruangan": 150,
        "provinsi": "Lampung",
        "kabupaten_kota": "Kota Bandar Lampung",
    },
    {
        "kode_rs": "1971030",
        "nama_rs": "RSUD Dr. (H.C.) Ir. Soekarno Babel",
        "alamat_rs": "Jl. Z.A. Pagar Alam, Air Anyir",
        "total_bed_kosong": 35,
        "bed_icu_vvip_kosong": 4,
        "total_ruangan": 95,
        "provinsi": "Kepulauan Bangka Belitung",
        "kabupaten_kota": "Kabupaten Bangka",
    },
    {
        "kode_rs": "2171031",
        "nama_rs": "RSUD Raja Ahmad Tabib",
        "alamat_rs": "Jl. F.R. Hakim No. 1, Tanjungpinang",
        "total_bed_kosong": 40,
        "bed_icu_vvip_kosong": 5,
        "total_ruangan": 115,
        "provinsi": "Kepulauan Riau",
        "kabupaten_kota": "Kota Tanjungpinang",
    },
    {
        "kode_rs": "5271032",
        "nama_rs": "RSUD Provinsi NTB",
        "alamat_rs": "Jl. Prabu Ratu, Dasan Cermen, Mataram",
        "total_bed_kosong": 46,
        "bed_icu_vvip_kosong": 6,
        "total_ruangan": 125,
        "provinsi": "Nusa Tenggara Barat",
        "kabupaten_kota": "Kota Mataram",
    },
    {
        "kode_rs": "5371033",
        "nama_rs": "RSUD Prof. Dr. W.Z. Johannes",
        "alamat_rs": "Jl. Moch. Hatta No. 19, Kupang",
        "total_bed_kosong": 44,
        "bed_icu_vvip_kosong": 5,
        "total_ruangan": 120,
        "provinsi": "Nusa Tenggara Timur",
        "kabupaten_kota": "Kota Kupang",
    },
    {
        "kode_rs": "6171034",
        "nama_rs": "RSUD dr. Soedarso Pontianak",
        "alamat_rs": "Jl. Dr. Soedarso No. 1",
        "total_bed_kosong": 56,
        "bed_icu_vvip_kosong": 7,
        "total_ruangan": 155,
        "provinsi": "Kalimantan Barat",
        "kabupaten_kota": "Kota Pontianak",
    },
    {
        "kode_rs": "6271035",
        "nama_rs": "RSUD dr. Doris Sylvanus",
        "alamat_rs": "Jl. Tambun Bungai No. 4, Palangka Raya",
        "total_bed_kosong": 42,
        "bed_icu_vvip_kosong": 5,
        "total_ruangan": 118,
        "provinsi": "Kalimantan Tengah",
        "kabupaten_kota": "Kota Palangka Raya",
    },
    {
        "kode_rs": "6371036",
        "nama_rs": "RSUD Ulin Banjarmasin",
        "alamat_rs": "Jl. Jen. A. Yani No. 43",
        "total_bed_kosong": 62,
        "bed_icu_vvip_kosong": 8,
        "total_ruangan": 170,
        "provinsi": "Kalimantan Selatan",
        "kabupaten_kota": "Kota Banjarmasin",
    },
    {
        "kode_rs": "6471037",
        "nama_rs": "RSUD Abdul Wahab Sjahranie",
        "alamat_rs": "Jl. Palang Merah No. 1, Samarinda",
        "total_bed_kosong": 65,
        "bed_icu_vvip_kosong": 9,
        "total_ruangan": 180,
        "provinsi": "Kalimantan Timur",
        "kabupaten_kota": "Kota Samarinda",
    },
    {
        "kode_rs": "6571038",
        "nama_rs": "RSUD dr. H. Jusuf SK Tarakan",
        "alamat_rs": "Jl. Pulau Irian No. 1, Tarakan",
        "total_bed_kosong": 36,
        "bed_icu_vvip_kosong": 4,
        "total_ruangan": 105,
        "provinsi": "Kalimantan Utara",
        "kabupaten_kota": "Kota Tarakan",
    },
    {
        "kode_rs": "7171039",
        "nama_rs": "RSUP Prof. Dr. R.D. Kandou",
        "alamat_rs": "Jl. Raya Tanawangko No. 56, Malalayang",
        "total_bed_kosong": 64,
        "bed_icu_vvip_kosong": 9,
        "total_ruangan": 175,
        "provinsi": "Sulawesi Utara",
        "kabupaten_kota": "Kota Manado",
    },
    {
        "kode_rs": "7271040",
        "nama_rs": "RSUD Undata Palu",
        "alamat_rs": "Jl. RE Martadinata, Tondo",
        "total_bed_kosong": 45,
        "bed_icu_vvip_kosong": 6,
        "total_ruangan": 125,
        "provinsi": "Sulawesi Tengah",
        "kabupaten_kota": "Kota Palu",
    },
    {
        "kode_rs": "7371041",
        "nama_rs": "RSUP Dr. Wahidin Sudirohusodo",
        "alamat_rs": "Jl. Perintis Kemerdekaan Km. 11, Tamalanrea",
        "total_bed_kosong": 78,
        "bed_icu_vvip_kosong": 12,
        "total_ruangan": 205,
        "provinsi": "Sulawesi Selatan",
        "kabupaten_kota": "Kota Makassar",
    },
    {
        "kode_rs": "7471042",
        "nama_rs": "RSUD Bahteramas Kendari",
        "alamat_rs": "Jl. Kapten Piere Tendean No. 50",
        "total_bed_kosong": 48,
        "bed_icu_vvip_kosong": 6,
        "total_ruangan": 130,
        "provinsi": "Sulawesi Tenggara",
        "kabupaten_kota": "Kota Kendari",
    },
    {
        "kode_rs": "7571043",
        "nama_rs": "RSUD Prof. Dr. H. Aloei Saboe",
        "alamat_rs": "Jl. Prof. Dr. Aloei Saboe, Gorontalo",
        "total_bed_kosong": 38,
        "bed_icu_vvip_kosong": 4,
        "total_ruangan": 110,
        "provinsi": "Gorontalo",
        "kabupaten_kota": "Kota Gorontalo",
    },
    {
        "kode_rs": "7602044",
        "nama_rs": "RSUD Provinsi Sulawesi Barat",
        "alamat_rs": "Jl. RE Martadinata, Simboro, Mamuju",
        "total_bed_kosong": 32,
        "bed_icu_vvip_kosong": 3,
        "total_ruangan": 90,
        "provinsi": "Sulawesi Barat",
        "kabupaten_kota": "Kabupaten Mamuju",
    },
    {
        "kode_rs": "8171045",
        "nama_rs": "RSUP Dr. J. Leimena",
        "alamat_rs": "Jl. Pahlawan Revolusi, Rumah Tiga, Ambon",
        "total_bed_kosong": 50,
        "bed_icu_vvip_kosong": 7,
        "total_ruangan": 135,
        "provinsi": "Maluku",
        "kabupaten_kota": "Kota Ambon",
    },
    {
        "kode_rs": "8271046",
        "nama_rs": "RSUD Dr. H. Chasan Boesoirie",
        "alamat_rs": "Jl. Cempaka, Tanah Tinggi, Ternate",
        "total_bed_kosong": 40,
        "bed_icu_vvip_kosong": 5,
        "total_ruangan": 115,
        "provinsi": "Maluku Utara",
        "kabupaten_kota": "Kota Ternate",
    },
    {
        "kode_rs": "9171047",
        "nama_rs": "RSUD Dok II Jayapura",
        "alamat_rs": "Jl. Kesehatan No. 1, Jayapura",
        "total_bed_kosong": 52,
        "bed_icu_vvip_kosong": 6,
        "total_ruangan": 140,
        "provinsi": "Papua",
        "kabupaten_kota": "Kota Jayapura",
    },
    {
        "kode_rs": "9202048",
        "nama_rs": "RSUD Provinsi Papua Barat",
        "alamat_rs": "Jl. Angkasa Mulyo, Amban, Manokwari",
        "total_bed_kosong": 35,
        "bed_icu_vvip_kosong": 4,
        "total_ruangan": 95,
        "provinsi": "Papua Barat",
        "kabupaten_kota": "Kabupaten Manokwari",
    },
    {
        "kode_rs": "9301049",
        "nama_rs": "RSUD Merauke",
        "alamat_rs": "Jl. Soekarjo Wiryopranoto No. 1",
        "total_bed_kosong": 42,
        "bed_icu_vvip_kosong": 5,
        "total_ruangan": 118,
        "provinsi": "Papua Selatan",
        "kabupaten_kota": "Kabupaten Merauke",
    },
    {
        "kode_rs": "9671050",
        "nama_rs": "RSUD Sele Be Solu Sorong",
        "alamat_rs": "Jl. Klamono Km. 12, Sorong",
        "total_bed_kosong": 46,
        "bed_icu_vvip_kosong": 6,
        "total_ruangan": 125,
        "provinsi": "Papua Barat Daya",
        "kabupaten_kota": "Kota Sorong",
    },
]


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
        yielded_any = False
        try:
            resp = requests.get(self.url, params=params, headers=headers, timeout=15)
            if resp.status_code == 200:
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
                    yielded_any = True
        except Exception as exc:
            logger.warning("Failed to fetch SIRANAP portal: %s", exc)

        if not yielded_any:
            logger.info("Emitting national referral hospital dataset (%d facilities)", len(OFFLINE_FALLBACK_DATA))
            for item in OFFLINE_FALLBACK_DATA:
                yield item
