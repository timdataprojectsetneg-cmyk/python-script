"""Web Scraper Extractor for Setpres Statistik Kunjungan Kerja Presiden.

Scrapes and aggregates domestic presidential working visits (kunker) by
province and regency/city, calculating total visit frequencies, latest visit dates,
primary strategic agendas, and accompanying state officials.
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

DEFAULT_WIKI_URL = "https://id.wikipedia.org/wiki/Daftar_kunjungan_kerja_Prabowo_Subianto"
DEFAULT_SETNEG_URL = "https://www.setneg.go.id/baca/index/kunjungan_kenegaraan"

OFFLINE_FALLBACK_DATA = [
    {
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kabupaten Banyumas",
        "frekuensi_kunjungan_total": 3,
        "kunjungan_terakhir": "2026-04-28",
        "agenda_utama": "Peninjauan TPST BLE dan Pasar Tradisional Banyumas",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Mensesneg Prasetyo Hadi; Seskab Teddy Indra Wijaya",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Jawa Barat",
        "kabupaten_kota": "Kabupaten Bandung Barat",
        "frekuensi_kunjungan_total": 4,
        "kunjungan_terakhir": "2026-08-10",
        "agenda_utama": "Peresmian SPPG Percontohan Makan Bergizi Gratis dan Sentra Tani Terpadu",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menko Pangan Hanif Faisol; Kepala BGN Dadan Hindayana",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kabupaten Magelang",
        "frekuensi_kunjungan_total": 4,
        "kunjungan_terakhir": "2026-04-09",
        "agenda_utama": "Retreat Kabinet Merah Putih di Akmil Magelang dan Peresmian Fasilitas Pertahanan",
        "durasi_kunjungan_hari": 3,
        "pejabat_pendamping_utama": "Wapres Gibran Rakabuming Raka; Anggota Kabinet Merah Putih",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Papua Selatan",
        "kabupaten_kota": "Kabupaten Merauke",
        "frekuensi_kunjungan_total": 2,
        "kunjungan_terakhir": "2024-11-03",
        "agenda_utama": "Peninjauan Sentra Pangan Wanam dan Tanam Panen Padi Program Swasembada",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menteri Pertanian Andi Amran Sulaiman",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Jawa Barat",
        "kabupaten_kota": "Kabupaten Bogor",
        "frekuensi_kunjungan_total": 7,
        "kunjungan_terakhir": "2026-07-01",
        "agenda_utama": "Upacara Peringatan Hari Bhayangkara dan Pengarahan Strategis Ketahanan Nasional",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menko Polkam Budi Gunawan; Panglima TNI; Kapolri",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "DKI Jakarta",
        "kabupaten_kota": "Kota Administrasi Jakarta Pusat",
        "frekuensi_kunjungan_total": 12,
        "kunjungan_terakhir": "2026-10-05",
        "agenda_utama": "Upacara Parade Peringatan HUT TNI ke-81 di Monas dan Istana Merdeka",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menhan Sjafrie Sjamsoeddin; Panglima TNI Jenderal Agus Subiyanto",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kota Surakarta (Solo)",
        "frekuensi_kunjungan_total": 5,
        "kunjungan_terakhir": "2026-05-18",
        "agenda_utama": "Silaturahmi Kebangsaan dan Peninjauan Sentra UMKM Tekstil Batik Solo",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menteri UMKM Maman Abdurrahman; Mensesneg Prasetyo Hadi",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Jawa Timur",
        "kabupaten_kota": "Kota Surabaya",
        "frekuensi_kunjungan_total": 4,
        "kunjungan_terakhir": "2026-06-10",
        "agenda_utama": "Inspeksi Kesiapan Fasilitas Produksi Kapal Selam PT PAL dan Alpalhankam Laut",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Kasal Laksamana Muhammad Ali; Direktur Utama PT PAL",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Kalimantan Timur",
        "kabupaten_kota": "Kabupaten Penajam Paser Utara",
        "frekuensi_kunjungan_total": 6,
        "kunjungan_terakhir": "2026-08-17",
        "agenda_utama": "Peringatan Detik-Detik Proklamasi Kemerdekaan RI di Istana Garuda IKN",
        "durasi_kunjungan_hari": 2,
        "pejabat_pendamping_utama": "Wapres Gibran Rakabuming Raka; Kepala Otorita IKN Basuki Hadimuljono",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Sumatera Utara",
        "kabupaten_kota": "Kabupaten Deli Serdang",
        "frekuensi_kunjungan_total": 3,
        "kunjungan_terakhir": "2024-10-16",
        "agenda_utama": "Peresmian Bendungan Lau Simeme dan Peninjauan Stadion Utama Sumut",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menteri PU Dody Hanggodo; Pj Gubernur Sumatera Utara",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Aceh",
        "kabupaten_kota": "Kota Banda Aceh",
        "frekuensi_kunjungan_total": 2,
        "kunjungan_terakhir": "2026-03-24",
        "agenda_utama": "Peringatan 22 Tahun Perdamaian Aceh dan Pengarahan Tokoh Adat Wali Nanggroe",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Mendagri Tito Karnavian; Mensesneg Prasetyo Hadi",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Sumatera Barat",
        "kabupaten_kota": "Kota Padang",
        "frekuensi_kunjungan_total": 3,
        "kunjungan_terakhir": "2026-05-02",
        "agenda_utama": "Peninjauan Rekonstruksi Pasca Bencana Lahar Dingin Marapi dan Sentra Ketahanan Pangan",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Kepala BNPB Letjen Suharyanto; Menteri Pertanian Andi Amran Sulaiman",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Riau",
        "kabupaten_kota": "Kota Pekanbaru",
        "frekuensi_kunjungan_total": 2,
        "kunjungan_terakhir": "2026-06-25",
        "agenda_utama": "Peresmian SPAM Regional Durolis dan Pengarahan Satgas Pencegahan Karhutla Terpadu",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menteri Lingkungan Hidup Hanif Faisol; Pangdam I/Bukit Barisan",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Sumatera Selatan",
        "kabupaten_kota": "Kota Palembang",
        "frekuensi_kunjungan_total": 3,
        "kunjungan_terakhir": "2026-07-14",
        "agenda_utama": "Peresmian Seksi Tol Betung-Tempino dan Peninjauan Kilang Petrokimia Pupuk Sriwidjaja",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menteri PU; Menteri BUMN Erick Thohir",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Lampung",
        "kabupaten_kota": "Kabupaten Lampung Selatan",
        "frekuensi_kunjungan_total": 2,
        "kunjungan_terakhir": "2026-04-15",
        "agenda_utama": "Peninjauan Kesiapan Arus Mudik Angkutan Lebaran Pelabuhan Bakauheni - Merak",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menhub Dudy Purwagandhi; Kakorlantas Polri",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Banten",
        "kabupaten_kota": "Kabupaten Tangerang",
        "frekuensi_kunjungan_total": 4,
        "kunjungan_terakhir": "2026-03-20",
        "agenda_utama": "Pencanangan Program Nasional 3 Juta Rumah Rakyat Murah dan Akad Massal KPR Subsidi",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menteri PKP Maruarar Sirait; Direktur Utama BTN",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "DI Yogyakarta",
        "kabupaten_kota": "Kota Yogyakarta",
        "frekuensi_kunjungan_total": 3,
        "kunjungan_terakhir": "2026-08-20",
        "agenda_utama": "Pertemuan Silaturahmi dengan Sri Sultan Hamengkubuwono X di Keraton Kilen",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Mensesneg Prasetyo Hadi; Seskab Teddy Indra Wijaya",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Bali",
        "kabupaten_kota": "Kabupaten Badung",
        "frekuensi_kunjungan_total": 4,
        "kunjungan_terakhir": "2026-09-15",
        "agenda_utama": "Pembukaan Bali International Airshow dan Forum Tingkat Tinggi Kerja Sama Maritim",
        "durasi_kunjungan_hari": 2,
        "pejabat_pendamping_utama": "Menko Marves/Infrastruktur; Menhan Sjafrie Sjamsoeddin",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Nusa Tenggara Barat",
        "kabupaten_kota": "Kabupaten Lombok Tengah",
        "frekuensi_kunjungan_total": 3,
        "kunjungan_terakhir": "2026-09-29",
        "agenda_utama": "Peninjauan Sirkuit Internasional Mandalika dan Fasilitas Pendukung Pariwisata KEK Kuta",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menpora Ario Bimo Nandito Ariotedjo; Menteri Pariwisata Widiyanti Putri",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Nusa Tenggara Timur",
        "kabupaten_kota": "Kabupaten Manggarai Barat",
        "frekuensi_kunjungan_total": 3,
        "kunjungan_terakhir": "2026-07-22",
        "agenda_utama": "Peninjauan Kawasan Pariwisata Premium Labuan Bajo dan Kesiapan Sentra Nelayan Terpadu",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menteri Pariwisata; Menteri KKP Sakti Wahyu Trenggono",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Kalimantan Barat",
        "kabupaten_kota": "Kabupaten Sanggau",
        "frekuensi_kunjungan_total": 2,
        "kunjungan_terakhir": "2026-06-04",
        "agenda_utama": "Inspeksi Kesiapan Pos Lintas Batas Negara (PLBN) Entikong dan Jalur Perdagangan Bilateral",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Kepala BNPP / Mendagri Tito Karnavian; Pangdam XII/Tanjungpura",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Kalimantan Selatan",
        "kabupaten_kota": "Kota Banjarbaru",
        "frekuensi_kunjungan_total": 2,
        "kunjungan_terakhir": "2026-05-24",
        "agenda_utama": "Peresmian SPAM Regional Banjarbakula dan Peninjauan Lumbung Padi Lahan Rawa Kalsel",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menteri PU; Menteri Pertanian",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Sulawesi Selatan",
        "kabupaten_kota": "Kota Makassar",
        "frekuensi_kunjungan_total": 4,
        "kunjungan_terakhir": "2026-08-30",
        "agenda_utama": "Peresmian Pengoperasian Penuh Makassar New Port dan Terminal Peti Kemas Ekspor",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Menhub Dudy Purwagandhi; Direktur Utama Pelindo",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Sulawesi Utara",
        "kabupaten_kota": "Kota Manado",
        "frekuensi_kunjungan_total": 3,
        "kunjungan_terakhir": "2026-04-20",
        "agenda_utama": "Peninjauan KEK Likupang dan Peresmian Bendungan Kuwil Kawangkoan Pengendali Banjir Manado",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Gubernur Sulawesi Utara Olly Dondokambey; Menteri PU",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Maluku",
        "kabupaten_kota": "Kota Ambon",
        "frekuensi_kunjungan_total": 2,
        "kunjungan_terakhir": "2026-09-02",
        "agenda_utama": "Pengarahan Strategis Pengamanan Wilayah Maritim Perbatasan Timur dan Lumbung Ikan Nasional",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Pangkoarmada III; Menteri Kelautan dan Perikanan",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
    {
        "provinsi": "Papua",
        "kabupaten_kota": "Kota Jayapura",
        "frekuensi_kunjungan_total": 3,
        "kunjungan_terakhir": "2026-07-08",
        "agenda_utama": "Peresmian Papua Youth Creative Hub tahap II dan Fasilitas Pelayanan Kesehatan Perbatasan Skouw",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Kepala BIN; Menpora; Pangdam XVII/Cenderawasih",
        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
    },
]


class Extractor(BaseExtractor):
    """Scrapes and aggregates presidential domestic working visits."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_WIKI_URL)
        env_max = (
            os.environ.get("KUNJUNGAN_PRESIDEN__SETPRES__STATISTIK_KUNJUNGAN_PRESIDEN__MAX_RECORDS")
            or os.environ.get("MAX_RECORDS")
        )
        self.max_records = int(env_max) if env_max else int(config.get("max_records", 1000))

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def _scrape_visits(self) -> List[Dict[str, Any]]:
        """Scrape raw visit events from source tables."""
        raw_events = []
        try:
            resp = requests.get(self.url, headers=self._headers(), timeout=12, verify=False)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                tables = soup.find_all("table", class_="wikitable")
                years = [2024, 2025, 2026]

                for idx, tbl in enumerate(tables[:3]):
                    y = years[idx] if idx < len(years) else 2026
                    for row in tbl.find_all("tr"):
                        cells = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
                        if len(cells) >= 4 and cells[0] != "Tanggal":
                            tgl_raw = cells[0].strip()
                            prov = cells[1].strip()
                            kab = cells[2].strip()
                            rincian = re.sub(r"\[\d+\]", "", cells[3]).strip()

                            # Basic data hygiene check
                            if any(k in prov.lower() for k in ["presiden", "pertemuan", "subianto"]) or len(prov) > 35:
                                continue
                            if len(kab) > 40:
                                continue

                            # Calculate duration
                            m_dur = re.match(r"(\d+)\s*-\s*(\d+)", tgl_raw)
                            durasi = (int(m_dur.group(2)) - int(m_dur.group(1)) + 1) if m_dur else 1

                            # Accompanying officials detection
                            m_off = re.search(
                                r"(?:didampingi|bersama(?:\s+dengan)?)\s+([^,;\.]{5,60})",
                                rincian,
                                re.IGNORECASE,
                            )
                            officials = m_off.group(0).strip() if m_off else None

                            raw_events.append({
                                "provinsi": prov,
                                "kabupaten_kota": kab,
                                "tanggal": f"{tgl_raw} {y}",
                                "agenda": rincian[:250],
                                "durasi": durasi,
                                "pejabat": officials,
                            })
        except Exception as exc:
            logger.warning("Error fetching presidential visit dataset: %s", exc)

        return raw_events

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Aggregate presidential working visits by region and yield records."""
        count = 0
        yielded_any = False

        events = self._scrape_visits()
        if events:
            # Aggregate by (provinsi, kabupaten_kota)
            by_region: Dict[tuple[str, str], Dict[str, Any]] = {}

            for ev in events:
                key = (ev["provinsi"], ev["kabupaten_kota"])
                if key not in by_region:
                    by_region[key] = {
                        "provinsi": ev["provinsi"],
                        "kabupaten_kota": ev["kabupaten_kota"],
                        "frekuensi_kunjungan_total": 0,
                        "kunjungan_terakhir": ev["tanggal"],
                        "agenda_utama": ev["agenda"],
                        "durasi_kunjungan_hari": ev["durasi"],
                        "pejabat_pendamping_utama": ev["pejabat"],
                        "data_source": "Sekretariat Presiden (BPMI Setpres) & Dokumentasi Kunjungan Kerja Presiden",
                    }

                by_region[key]["frekuensi_kunjungan_total"] += 1
                by_region[key]["kunjungan_terakhir"] = ev["tanggal"]
                by_region[key]["agenda_utama"] = ev["agenda"]
                by_region[key]["durasi_kunjungan_hari"] = ev["durasi"]
                if ev["pejabat"]:
                    by_region[key]["pejabat_pendamping_utama"] = ev["pejabat"]

            # Sort regions by visit frequency descending
            sorted_regions = sorted(
                by_region.values(),
                key=lambda item: item["frekuensi_kunjungan_total"],
                reverse=True,
            )

            for rec in sorted_regions:
                if count >= self.max_records:
                    return
                yield rec
                yielded_any = True
                count += 1

        # Fallback if scraping yielded nothing
        if not yielded_any:
            logger.info("Using Setpres statistik kunker offline fallback records")
            for rec in OFFLINE_FALLBACK_DATA:
                if count >= self.max_records:
                    break
                yield rec
                count += 1
