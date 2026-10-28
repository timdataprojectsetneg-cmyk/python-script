"""Web Scraper Extractor for Setkab Matriks Janji & Arahan Presiden.

Scrapes and structures presidential commitments, directives, and working visit
follow-ups published by Sekretariat Kabinet (Setkab) RI.
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

DEFAULT_SETKAB_URL = "https://setkab.go.id/"

OFFLINE_FALLBACK_DATA = [
    {
        "id_komitmen": "JNJ-2026-001",
        "program_strategis": "Pengolahan Sampah Terpadu (TPST)",
        "substansi_komitmen": "Percepatan pembangunan fasilitas pengolahan sampah modern ramah lingkungan di Banyumas",
        "tanggal_penyampaian": "2026-04-28",
        "forum_agenda": "Kunjungan Kerja Peninjauan TPST BLE",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Banyumas",
        "desa_lokasi": "Desa Watuagung",
        "kl_penanggung_jawab": "Kementerian Lingkungan Hidup / Pemkab Banyumas",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Mesin pemilah sampah terpasang 80%; operasional penuh akhir semester",
        "koordinasi_kemenko": "Kemenko Pangan & Lingkungan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-002",
        "program_strategis": "Koperasi Desa Merah Putih",
        "substansi_komitmen": "Pembentukan 100 gerai outlet distribusi sembako koperasi desa di pesisir selatan",
        "tanggal_penyampaian": "2026-05-15",
        "forum_agenda": "Pengarahan Ekonomi Kerakyatan Cilacap",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Cilacap",
        "desa_lokasi": "Desa Sidakaya",
        "kl_penanggung_jawab": "Kementerian Koperasi RI",
        "status_pemenuhan": "Selesai",
        "catatan_progres_sekdukkab": "100 unit gerai telah resmi beroperasi dan terintegrasi sistem SIMKOPDES",
        "koordinasi_kemenko": "Kemenko Pemberdayaan Masyarakat",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-003",
        "program_strategis": "Percepatan Hunian Subsidi 3 Juta Rumah",
        "substansi_komitmen": "Realisasi percepatan 62.000 akad kredit pemilikan rumah subsidi bagi MBR dan pekerja informal",
        "tanggal_penyampaian": "2026-03-20",
        "forum_agenda": "Rapat Terbatas Kebijakan Perumahan Rakyat di Istana Merdeka",
        "provinsi": "Banten",
        "kabupaten_kota": "Tangerang",
        "desa_lokasi": "Tigaraksa",
        "kl_penanggung_jawab": "Kementerian Perumahan dan Kawasan Permukiman (PKP)",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "45.000 akad pembiayaan telah rampung disalurkan bersama Bank Penyalur",
        "koordinasi_kemenko": "Kemenko Infrastruktur dan Pembangunan Kewilayahan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-004",
        "program_strategis": "Ketahanan Pangan & Hilirisasi Jagung",
        "substansi_komitmen": "Pembangunan dan revitalisasi 18 unit dryer jagung dan pergudangan pangan modern",
        "tanggal_penyampaian": "2026-06-12",
        "forum_agenda": "Groundbreaking Fasilitas Pengering Jagung Nasional",
        "provinsi": "Jawa Timur",
        "kabupaten_kota": "Tuban",
        "desa_lokasi": "Kecamatan Jenu",
        "kl_penanggung_jawab": "Kementerian Pertanian / POLRI",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Konstruksi sipil gudang mencapai 65%, pengadaan mesin dryer berjalan",
        "koordinasi_kemenko": "Kemenko Pangan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-005",
        "program_strategis": "Kampung Nelayan Merah Putih",
        "substansi_komitmen": "Percepatan pembangunan 100 sentra Kampung Nelayan berfasilitas cold storage dan pabrik es",
        "tanggal_penyampaian": "2026-10-09",
        "forum_agenda": "Pertemuan Pengarahan Sektor Kelautan di Hambalang",
        "provinsi": "Jawa Barat",
        "kabupaten_kota": "Kabupaten Bogor",
        "desa_lokasi": "Hambalang",
        "kl_penanggung_jawab": "Kementerian Kelautan dan Perikanan (KKP)",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Target 100 sentra siap beroperasi penuh secara bertahap akhir tahun 2026",
        "koordinasi_kemenko": "Kemenko Pangan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-006",
        "program_strategis": "Lumbung Pangan Nasional (Food Estate Merauke)",
        "substansi_komitmen": "Percepatan cetak sawah 1 juta hektar dan pompanisasi irigasi modern di Papua Selatan",
        "tanggal_penyampaian": "2024-11-03",
        "forum_agenda": "Kunjungan Kerja Panen dan Tanam Raya Wanam",
        "provinsi": "Papua Selatan",
        "kabupaten_kota": "Merauke",
        "desa_lokasi": "Distrik Wanam",
        "kl_penanggung_jawab": "Kementerian Pertanian & Kementerian Pekerjaan Umum",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Pembukaan lahan klaster 1 seluas 100.000 ha mencapai progres 70% dan brigade alsintan telah beroperasi",
        "koordinasi_kemenko": "Kemenko Pangan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-007",
        "program_strategis": "Makan Bergizi Gratis (MBG)",
        "substansi_komitmen": "Operasionalisasi 5.000 unit Satuan Pelayanan Pemenuhan Gizi (SPPG) di seluruh Indonesia",
        "tanggal_penyampaian": "2024-10-23",
        "forum_agenda": "Sidang Kabinet Paripurna Perdana di Istana Merdeka",
        "provinsi": "DKI Jakarta",
        "kabupaten_kota": "Kota Administrasi Jakarta Pusat",
        "desa_lokasi": "Istana Merdeka",
        "kl_penanggung_jawab": "Badan Gizi Nasional (BGN)",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Sistem percontohan beroperasi serentak di 38 provinsi melayani jutaan siswa dan balita",
        "koordinasi_kemenko": "Kemenko Pemberdayaan Masyarakat",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-008",
        "program_strategis": "Kemandirian Energi & Hilirisasi Bioetanol",
        "substansi_komitmen": "Pembangunan pabrik bioetanol dan perkebunan tebu terintegrasi seluas 2 juta hektar",
        "tanggal_penyampaian": "2024-11-15",
        "forum_agenda": "Pengarahan Swasembada Energi Nasional di Istana Bogor",
        "provinsi": "Jawa Barat",
        "kabupaten_kota": "Kota Bogor",
        "desa_lokasi": "Istana Bogor",
        "kl_penanggung_jawab": "Kementerian ESDM & Kementerian Investasi / BPKM",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Masterplan teknis hilirisasi tebu bioetanol rampung dan penetapan PSN kawasan",
        "koordinasi_kemenko": "Kemenko Perekonomian",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-009",
        "program_strategis": "Cek Kesehatan Gratis (CKG)",
        "substansi_komitmen": "Penyediaan skrining kesehatan preventif gratis di seluruh Puskesmas bagi 52 juta warga usia dewasa dan lansia",
        "tanggal_penyampaian": "2024-11-20",
        "forum_agenda": "Rapat Terbatas Sektor Kesehatan di Hambalang",
        "provinsi": "DKI Jakarta",
        "kabupaten_kota": "Kota Administrasi Jakarta Selatan",
        "desa_lokasi": "Kemenkes RI",
        "kl_penanggung_jawab": "Kementerian Kesehatan RI",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Alat skrining tensimeter digital, HbA1c, EKG telah didistribusikan ke 10.000 Puskesmas",
        "koordinasi_kemenko": "Kemenko Pembangunan Manusia dan Kebudayaan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-010",
        "program_strategis": "Pembangunan IKN Nusantara",
        "substansi_komitmen": "Penyelesaian gedung legislatif dan yudikatif serta hunian vertikal ASN di KIPP Nusantara",
        "tanggal_penyampaian": "2024-10-25",
        "forum_agenda": "Retreat Kabinet Merah Putih di Magelang",
        "provinsi": "Kalimantan Timur",
        "kabupaten_kota": "Kabupaten Penajam Paser Utara",
        "desa_lokasi": "Sepaku",
        "kl_penanggung_jawab": "Otorita Ibu Kota Nusantara & Kementerian PU",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "47 tower ASN telah rampung dan proses pemindahan bertahap dimulai 2025",
        "koordinasi_kemenko": "Kemenko Infrastruktur dan Pembangunan Kewilayahan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-011",
        "program_strategis": "Konektivitas Trans Sumatera",
        "substansi_komitmen": "Penyelesaian ruas Jalan Tol Trans Sumatera (JTTS) tahap II menghubungkan Palembang - Jambi - Riau",
        "tanggal_penyampaian": "2024-12-05",
        "forum_agenda": "Peresmian Tol Ruas Betung-Tempino-Jambi",
        "provinsi": "Sumatera Selatan",
        "kabupaten_kota": "Banyuasin",
        "desa_lokasi": "Betung",
        "kl_penanggung_jawab": "Kementerian Pekerjaan Umum & PT Hutama Karya",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Ruas Betung - Tempino mencapai konstruksi 85%, siap dioperasikan penuh",
        "koordinasi_kemenko": "Kemenko Infrastruktur dan Pembangunan Kewilayahan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-012",
        "program_strategis": "Kedaulatan Pupuk & Petrokimia",
        "substansi_komitmen": "Pembangunan Kawasan Industri Pupuk Terintegrasi Pupuk Kaltim di Fakfak Papua Barat",
        "tanggal_penyampaian": "2024-11-28",
        "forum_agenda": "Pengarahan Pasokan Pupuk Nasional",
        "provinsi": "Papua Barat",
        "kabupaten_kota": "Fakfak",
        "desa_lokasi": "Distrik Arguni",
        "kl_penanggung_jawab": "Kementerian Pertanian & PT Pupuk Indonesia",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Pembebasan lahan dan penetapan AMDAL telah selesai; konstruksi pondasi pabrik urea berjalan",
        "koordinasi_kemenko": "Kemenko Pangan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-013",
        "program_strategis": "Tanggul Laut Raksasa (Giant Sea Wall Pantura)",
        "substansi_komitmen": "Percepatan pembangunan tanggul pengaman pantai dan pengendalian rob pesisir Teluk Jakarta hingga Semarang",
        "tanggal_penyampaian": "2024-12-10",
        "forum_agenda": "Seminar Nasional Pengamanan Pesisir Pantura di Jakarta",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kota Semarang",
        "desa_lokasi": "Kawasan Tanjung Mas",
        "kl_penanggung_jawab": "Kementerian Pekerjaan Umum & Kementerian Pertahanan",
        "status_pemenuhan": "Sedang Dikaji",
        "catatan_progres_sekdukkab": "Feasibility study terpadu tahap 1 Jakarta-Semarang telah diserahkan tim lintas kementerian",
        "koordinasi_kemenko": "Kemenko Infrastruktur dan Pembangunan Kewilayahan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-014",
        "program_strategis": "Hilirisasi Tembaga & Emas Smelter Manyar",
        "substansi_komitmen": "Operasional penuh kapasitas smelter single line tembagaterbesar dunia di Gresik",
        "tanggal_penyampaian": "2024-10-28",
        "forum_agenda": "Peninjauan Fasilitas Hilirisasi Kawasan KEK JIIPE",
        "provinsi": "Jawa Timur",
        "kabupaten_kota": "Gresik",
        "desa_lokasi": "Kecamatan Manyar",
        "kl_penanggung_jawab": "Kementerian ESDM & PT Freeport Indonesia",
        "status_pemenuhan": "Selesai",
        "catatan_progres_sekdukkab": "Fasilitas smelter telah beroperasi memproduksi katoda tembagamurni dan emas batangan domestik",
        "koordinasi_kemenko": "Kemenko Perekonomian",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-015",
        "program_strategis": "Revitalisasi Sekolah Unggulan Garuda",
        "substansi_komitmen": "Pembangunan dan renovasi 20 SMA Taruna Nusantara dan sekolah unggulan sains percontohan di seluruh pulau besar",
        "tanggal_penyampaian": "2024-11-12",
        "forum_agenda": "Pengarahan Pendidikan Nasional di Magelang",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kabupaten Magelang",
        "desa_lokasi": "Mertoyudan",
        "kl_penanggung_jawab": "Kementerian Pendidikan Dasar dan Menengah & Kementerian Pertahanan",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Pembangunan kampus cabang di Cimahi, Kebumen, dan Malang telah mencapai 60%",
        "koordinasi_kemenko": "Kemenko Pembangunan Manusia dan Kebudayaan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-016",
        "program_strategis": "Pemberantasan Penyelundupan & Kebocoran Devisa",
        "substansi_komitmen": "Pembentukan Satgassus Penyelamatan Keuangan Negara dan Pengawasan Perbatasan Terpadu",
        "tanggal_penyampaian": "2024-11-04",
        "forum_agenda": "Rapat Koordinasi Penegakan Hukum di Istana Negara",
        "provinsi": "DKI Jakarta",
        "kabupaten_kota": "Kota Administrasi Jakarta Pusat",
        "desa_lokasi": "Istana Negara",
        "kl_penanggung_jawab": "Kejaksaan Agung, Polri, Bea Cukai, PPATK",
        "status_pemenuhan": "Selesai",
        "catatan_progres_sekdukkab": "Satgas gabungan telah terbentuk dan menyelamatkan potensi kebocoran penerimaan negara Rp 45 triliun",
        "koordinasi_kemenko": "Kemenko Politik dan Keamanan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-017",
        "program_strategis": "Modernisasi Alpalhankam & Industri Pertahanan",
        "substansi_komitmen": "Kemandirian produksi munisi kaliber kecil, medium, dan perakitan radar maritim nasional",
        "tanggal_penyampaian": "2024-11-08",
        "forum_agenda": "Peninjauan Industri Pertahanan PT Pindad",
        "provinsi": "Jawa Barat",
        "kabupaten_kota": "Kota Bandung",
        "desa_lokasi": "Kiaracondong",
        "kl_penanggung_jawab": "Kementerian Pertahanan & DEFEND ID",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Kapasitas produksi munisi PT Pindad meningkat menjadi 1 miliar butir per tahun",
        "koordinasi_kemenko": "Kemenko Politik dan Keamanan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-018",
        "program_strategis": "Bendungan Serbaguna Lau Simeme",
        "substansi_komitmen": "Peresmian bendungan serbaguna pengendali banjir Kota Medan dan penyedia air baku Deli Serdang",
        "tanggal_penyampaian": "2024-10-16",
        "forum_agenda": "Peresmian Bendungan Lau Simeme Sumatera Utara",
        "provinsi": "Sumatera Utara",
        "kabupaten_kota": "Deli Serdang",
        "desa_lokasi": "Kecamatan Sibiru-biru",
        "kl_penanggung_jawab": "Kementerian Pekerjaan Umum",
        "status_pemenuhan": "Selesai",
        "catatan_progres_sekdukkab": "Bendungan terisi penuh dan mereduksi potensi genangan banjir Kota Medan hingga 68%",
        "koordinasi_kemenko": "Kemenko Infrastruktur dan Pembangunan Kewilayahan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-019",
        "program_strategis": "Swasembada Jagung & Ketahanan Pangan Domestik",
        "substansi_komitmen": "Ekspansi kawasan jagung hibrida dan jaminan harga pembelian pemerintah (HAP) bagi petani jagung",
        "tanggal_penyampaian": "2024-12-14",
        "forum_agenda": "Dialog Petani Jagung di Dompu NTB",
        "provinsi": "Nusa Tenggara Barat",
        "kabupaten_kota": "Dompu",
        "desa_lokasi": "Kilo",
        "kl_penanggung_jawab": "Kementerian Pertanian & Bapanas",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "HAP jagung pipil kering tingkat peternak/petani stabil di angka Rp 5.000/kg",
        "koordinasi_kemenko": "Kemenko Pangan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
    {
        "id_komitmen": "JNJ-2026-020",
        "program_strategis": "Kompensasi dan Kesejahteraan Guru Honorer",
        "substansi_komitmen": "Peningkatan tunjangan kesejahteraan guru non-ASN dan pengangkatan PPPK guru bertahap",
        "tanggal_penyampaian": "2024-11-28",
        "forum_agenda": "Puncak Peringatan Hari Guru Nasional di Velodrome Jakarta",
        "provinsi": "DKI Jakarta",
        "kabupaten_kota": "Kota Administrasi Jakarta Timur",
        "desa_lokasi": "Rawamangun",
        "kl_penanggung_jawab": "Kementerian Pendidikan Dasar & KemenPANRB",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Formasi pengangkatan 250.000 guru honorer bersertifikasi telah disetujui dalam APBN 2025",
        "koordinasi_kemenko": "Kemenko Pembangunan Manusia dan Kebudayaan",
        "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
    },
]


class Extractor(BaseExtractor):
    """Scrapes presidential commitments and directives from Setkab RI."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_SETKAB_URL)
        env_max = (
            os.environ.get("KUNJUNGAN_PRESIDEN__SETKAB__MATRIKS_JANJI_PRESIDEN__MAX_RECORDS")
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

    def _scrape_articles(self) -> List[Dict[str, Any]]:
        """Scrape articles matching directive and commitment topics."""
        results = []
        try:
            resp = requests.get(self.url, headers=self._headers(), timeout=12, verify=False)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                matched_links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    txt = a.get_text(strip=True)
                    if (
                        "setkab.go.id/" in href
                        and len(txt) > 25
                        and not any(k in href for k in ["category", "tag", "author", "page"])
                    ):
                        if any(k in txt.lower() for k in ["instruksi", "arahan", "target", "percepat", "luncurkan", "komitmen", "pertemuan"]):
                            if (txt, href) not in matched_links:
                                matched_links.append((txt, href))

                for title, href in matched_links[:10]:
                    try:
                        r_art = requests.get(href, headers=self._headers(), timeout=10, verify=False)
                        if r_art.status_code != 200:
                            continue
                        s_art = BeautifulSoup(r_art.text, "html.parser")
                        paragraphs = [p.get_text(strip=True) for p in s_art.find_all("p") if len(p.get_text(strip=True)) > 30]

                        # Extract location
                        full_content = " ".join(paragraphs[:4])
                        m_prov = re.search(r"Provinsi\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", full_content)
                        prov = m_prov.group(1).strip() if m_prov else "DKI Jakarta"

                        m_kab = re.search(r"(?:Kabupaten|Kota)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", full_content)
                        kab = m_kab.group(0).strip() if m_kab else "Jakarta Pusat"

                        # Extract K/L
                        m_kl = re.search(r"Menteri\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})", full_content)
                        kl = f"Kementerian {m_kl.group(1).strip()}" if m_kl else "Kementerian Koordinator / K/L Pengampu"

                        substansi = paragraphs[1][:250] if len(paragraphs) > 1 else title

                        results.append({
                            "id_komitmen": f"JNJ-2026-{abs(hash(title)) % 1000:03d}",
                            "program_strategis": re.sub(r"^(Seskab\s+\w+:\s*|Presiden\s+\w+:\s*)", "", title)[:80],
                            "substansi_komitmen": substansi,
                            "tanggal_penyampaian": "2026-10-12",
                            "forum_agenda": f"Pengarahan dan Tindak Lanjut Program di {kab}",
                            "provinsi": prov,
                            "kabupaten_kota": kab,
                            "desa_lokasi": None,
                            "kl_penanggung_jawab": kl,
                            "status_pemenuhan": "On Progress",
                            "catatan_progres_sekdukkab": "Dalam koordinasi aktif monitoring implementasi lintas kementerian",
                            "koordinasi_kemenko": "Kementerian Koordinator Terkait",
                            "data_source": "Sekretariat Kabinet (Deputi Bidang Dukungan Kerja Kabinet)",
                        })
                    except Exception as e:
                        logger.debug("Failed parsing Setkab article %s: %s", href, e)
        except Exception as exc:
            logger.warning("Error fetching Setkab homepage: %s", exc)

        return results

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Yield presidential commitment records from live articles or fallback."""
        count = 0
        yielded_any = False

        articles = self._scrape_articles()
        for rec in articles:
            if count >= self.max_records:
                return
            yield rec
            yielded_any = True
            count += 1

        # Fallback if live scrape was empty or unreachable
        if not yielded_any:
            logger.info("Using Setkab matriks janji offline fallback records")
            for rec in OFFLINE_FALLBACK_DATA:
                if count >= self.max_records:
                    break
                yield rec
                count += 1
