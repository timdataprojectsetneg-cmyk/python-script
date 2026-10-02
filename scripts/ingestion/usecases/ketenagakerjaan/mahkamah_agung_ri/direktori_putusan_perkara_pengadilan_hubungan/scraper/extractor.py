"""Scraper access — Direktori Putusan Perkara Pengadilan Hubungan Industrial (Mahkamah Agung RI).

Ported from the standalone ``scripts/scrape_phi.py``. Crawls the MA putusan
directory (putusan3.mahkamahagung.go.id) PHI listing, opens each detail page,
and yields records matching ``models.Record`` (full detail nested under
``putusan``). Cloudflare ``TOKEN`` (sent as ``security_token``), ``COOKIE`` and
``USER_AGENT`` are read from the source environment (``scripts/.env.dev``); the
crawl size is fixed here (no CLI flags).
"""

from __future__ import annotations

import math
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from typing import Any, Dict, Iterator, List, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment

from ......core.base.extractor import BaseExtractor
from ......core.base.http import HttpClient
from ......exceptions import ConfigError, SourceUnavailable

BASE = "https://putusan3.mahkamahagung.go.id/"
SEARCH_URL = BASE + "search.html"

# Crawl size, pacing and concurrency are fixed in code for this source.
# ``None`` = read every page (page count derived from "Ditemukan N data", else
# from the paging widget); set an integer to cap the crawl (e.g. MAX_PAGES = 5).
MAX_PAGES: int | None = None
REQUEST_DELAY = 1.5
ROWS_PER_PAGE = 20
CONCURRENCY = 2  # listing pages processed in parallel

BULAN = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6,
    "juli": 7, "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12,
}

# label tabel detail (dinormalisasi) -> key di JSON `putusan`
DETAIL_MAP = {
    "nomor": "Nomor_Perkara",
    "tingkat proses": "Tingkat_Proses",
    "klasifikasi": "Klasifikasi",
    "kata kunci": "Kata_Kunci",
    "tahun": "Tahun",
    "lembaga peradilan": "Pengadilan",
    "jenis lembaga peradilan": "Jenis_Lembaga_Peradilan",
    "tanggal register": "Tanggal_Register",
    "tanggal musyawarah": "Tanggal_Musyawarah",
    "tanggal dibacakan": "Tanggal_Dibacakan",
    "tanggal upload": "Tanggal_Upload",
    "hakim ketua": "Hakim_Ketua",
    "hakim anggota": "Hakim_Anggota",
    "panitera": "Panitera",
    "panitera pengganti": "Panitera",
    "amar": "Amar",
    "amar lainnya": "Amar_Lainnya",
    "catatan amar": "Catatan_Amar",
    "kaidah": "Kaidah",
    "abstrak": "Abstrak",
    "penggugat": "Penggugat",
    "tergugat": "Tergugat",
}
PUTUSAN_KEYS = [
    "Nomor_Perkara", "Tingkat_Proses", "Klasifikasi", "Kata_Kunci", "Tahun", "Pengadilan",
    "Jenis_Lembaga_Peradilan", "Tanggal_Register", "Tanggal_Musyawarah", "Tanggal_Dibacakan",
    "Tanggal_Upload", "Hakim_Ketua", "Hakim_Anggota", "Panitera", "Penggugat", "Tergugat",
    "Amar", "Amar_Lainnya", "Catatan_Amar", "Kaidah", "Abstrak", "Status_Putusan_Listing",
]
DATE_KEYS = ["Tanggal_Register", "Tanggal_Musyawarah", "Tanggal_Dibacakan", "Tanggal_Upload"]

# kota/kode pengadilan -> provinsi (best effort; kosong jika tidak ketemu)
PROVINSI = {
    "banda aceh": "Aceh", "medan": "Sumatera Utara", "padang": "Sumatera Barat",
    "pekanbaru": "Riau", "tanjungpinang": "Kepulauan Riau", "batam": "Kepulauan Riau",
    "jambi": "Jambi", "palembang": "Sumatera Selatan", "bengkulu": "Bengkulu",
    "tanjung karang": "Lampung", "bandar lampung": "Lampung",
    "pangkalpinang": "Kepulauan Bangka Belitung",
    "jakarta": "DKI Jakarta", "jkt": "DKI Jakarta",
    "serang": "Banten", "tangerang": "Banten",
    "bandung": "Jawa Barat", "bekasi": "Jawa Barat", "bogor": "Jawa Barat",
    "depok": "Jawa Barat", "cikarang": "Jawa Barat", "karawang": "Jawa Barat",
    "semarang": "Jawa Tengah", "surabaya": "Jawa Timur", "sidoarjo": "Jawa Timur",
    "malang": "Jawa Timur", "yogyakarta": "DI Yogyakarta", "denpasar": "Bali",
    "mataram": "Nusa Tenggara Barat", "kupang": "Nusa Tenggara Timur",
    "pontianak": "Kalimantan Barat", "palangkaraya": "Kalimantan Tengah",
    "banjarmasin": "Kalimantan Selatan", "samarinda": "Kalimantan Timur",
    "balikpapan": "Kalimantan Timur", "tarakan": "Kalimantan Utara",
    "manado": "Sulawesi Utara", "palu": "Sulawesi Tengah", "makassar": "Sulawesi Selatan",
    "kendari": "Sulawesi Tenggara", "gorontalo": "Gorontalo", "mamuju": "Sulawesi Barat",
    "ambon": "Maluku", "ternate": "Maluku Utara", "jayapura": "Papua",
    "manokwari": "Papua Barat", "sorong": "Papua Barat Daya",
}

# HEURISTIK sektor industri dari nama tergugat (lalu ringkasan). Urutan = prioritas.
SEKTOR = [
    ("Jasa Perhotelan", r"hotel|resort|villa|penginapan|hospitality"),
    ("Tekstil & Garmen", r"tekstil|textile|garmen|garment|konveksi|benang|sandang"),
    ("Manufaktur Otomotif", r"otomotif|automotive|motor\b|astra|honda|yamaha|suzuki|toyota|daihatsu|komponen kendaraan"),
    ("Logistik & Pergudangan", r"logistik|logistic|ekspedisi|cargo|kargo|pergudangan|angkutan|transportasi|pelayaran|shipping|kurir|express"),
    ("Perdagangan Ritel", r"ritel|retail|swalayan|supermarket|minimarket|indomaret|alfamart|alfa\b|\bmart\b|toko|perdagangan|dagang"),
    ("Perbankan & Keuangan", r"\bbank\b|finance|keuangan|asuransi|leasing|multifinance|pembiayaan|koperasi|sekuritas"),
    ("Perkebunan & Pertanian", r"perkebunan|sawit|plantation|agro|karet|pertanian"),
    ("Pertambangan & Energi", r"tambang|pertambangan|mining|batu ?bara|coal|nikel|migas|energi|listrik"),
    ("Konstruksi & Properti", r"konstruksi|kontraktor|construction|properti|property|real estate|pembangunan"),
    ("Kesehatan", r"rumah sakit|klinik|farma|medika|kesehatan"),
    ("Pendidikan", r"sekolah|universitas|institut|yayasan|pendidikan"),
    ("Telekomunikasi & TI", r"telekomunikasi|telkom|teknologi|digital|software|informatika"),
    ("Manufaktur Lainnya", r"pabrik|manufaktur|industri|industries|\bindo[a-z]*\b.*(plastik|kimia|baja)"),
]

STATUS_RE = re.compile(r"(belum berkekuatan hukum tetap|berkekuatan hukum tetap|inkracht)", re.I)
NOMOR_RE = re.compile(r"Nomor\s+(\d+\s?K?/Pdt\.Sus[\w\-./]*(?:\s+PN\s+[A-Za-z.]+)?)", re.I)


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_date(text: Any) -> str:
    """'11-08-2021' | '11/08/2021' | '2021-08-11' | '11 Agustus 2021' -> 'YYYY-MM-DD'."""
    t = clean(text).lower()
    if not t or t == "-":
        return ""
    t = re.sub(r"^[a-z']+,\s*", "", t)  # buang nama hari
    m = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", t)
    if m:
        d, mo, y = map(int, m.groups())
    else:
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", t)
        if m:
            y, mo, d = map(int, m.groups())
        else:
            m = re.search(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", t)
            if not m or m.group(2) not in BULAN:
                return ""
            d, mo, y = int(m.group(1)), BULAN[m.group(2)], int(m.group(3))
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return ""


def hari_kerja(start_iso: str, end_iso: str) -> Any:
    """Hari kerja Senin-Jumat (end exclusive); libur nasional TIDAK dihitung."""
    if not start_iso or not end_iso:
        return ""
    try:
        start, end = date.fromisoformat(start_iso), date.fromisoformat(end_iso)
    except ValueError:
        return ""
    if end < start:
        return ""
    days = 0
    current = start
    while current < end:
        if current.weekday() < 5:
            days += 1
        current += timedelta(days=1)
    return days


def jenis_perselisihan(text: str) -> str:
    """HEURISTIK (tidak ada di situs): tebak dari teks judul/amar/abstrak."""
    t = (text or "").lower()
    if re.search(r"antar serikat|antar sp\b|serikat (pekerja|buruh).{0,40}serikat", t):
        return "Perselisihan Antar Serikat Pekerja"
    if re.search(r"pemutusan hubungan kerja|\bphk\b|pesangon|uang penghargaan|pensiun|mengundurkan diri", t):
        return "Perselisihan PHK"
    if re.search(r"perselisihan kepentingan|perjanjian kerja bersama|\bpkb\b|peraturan perusahaan|syarat[- ]syarat kerja", t):
        return "Perselisihan Kepentingan"
    if re.search(r"upah|lembur|\bthr\b|tunjangan|cuti|hak normatif|perselisihan hak|wanprestasi", t):
        return "Perselisihan Hak"
    return ""


def status_penyelesaian(catatan_amar: str, amar: str = "") -> str:
    """Normalisasi narasi amar -> Kabul Seluruhnya/Kabul Sebagian/Ditolak/Dicabut/Akta Perdamaian/Dading."""
    t = clean(catatan_amar or amar).lower()
    if not t:
        return ""
    if re.search(r"dading|akta perdamaian|putusan perdamaian|\bperdamaian\b", t):
        return "Akta Perdamaian/Dading"
    if re.search(r"dicabut|pencabutan|mencabut gugatan", t):
        return "Dicabut"
    if re.search(r"mengabulkan.{0,120}sebagian|dikabulkan sebagian|kabul sebagian", t):
        return "Kabul Sebagian"
    if re.search(r"mengabulkan|dikabulkan|kabul seluruh", t):
        return "Kabul Seluruhnya"
    if re.search(r"menolak|ditolak", t):
        return "Ditolak"
    if re.search(r"tidak dapat diterima|niet ontvankelijk|\bno\b", t):
        return "Tidak Dapat Diterima"
    return "Lainnya"


def sektor_industri(nama_tergugat: str, ringkasan: str = "") -> str:
    for text in (nama_tergugat or "", ringkasan or ""):
        t = text.lower()
        for label, pattern in SEKTOR:
            if re.search(pattern, t):
                return label
    return ""


def provinsi_dari(*sources: str) -> str:
    text = " ".join(s.lower() for s in sources if s)
    for key in sorted(PROVINSI, key=len, reverse=True):
        if re.search(r"(?<![a-z])" + re.escape(key), text):
            return PROVINSI[key]
    return ""


def _check_ascii(name: str, value: str) -> str:
    """Reject non-ASCII env values early (HTTP headers are latin-1, URLs ASCII).

    Catches truncated/mangled pastes (e.g. an ellipsis ``…``) with a clear message
    instead of a low-level ``UnicodeEncodeError`` from ``requests``.
    """
    for index, char in enumerate(value):
        if ord(char) > 127:
            raise ConfigError(
                f"{name} has a non-ASCII character {char!r} (U+{ord(char):04X}) at position "
                f"{index}; re-copy the full value from the browser (it looks truncated)."
            )
    return value


def _tidy_url(url: str) -> str:
    """Drop empty/dangling ``?``/``&`` left behind after removing a query param."""
    url = url.replace("?&", "?")
    while "&&" in url:
        url = url.replace("&&", "&")
    return url.rstrip("&").rstrip("?")


def page_url(base_url: str, page: int) -> str:
    """Return the search URL for a page, keeping ``security_token`` at the end."""
    url = _tidy_url(re.sub(r"[?&]page=\d+", "", base_url))
    if page <= 1:
        return url
    if "security_token=" in url:
        return url.replace("security_token=", f"page={page}&security_token=", 1)
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}page={page}"


def with_security_token(url: str, token: str) -> str:
    """Append ``&security_token=<token>`` at the very end of a search URL."""
    url = _tidy_url(re.sub(r"[?&]security_token=[^&]*", "", url))
    if not token:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}security_token={token}"


def is_phi_case(value: str) -> bool:
    """True when a case identifier/title contains ``PHI``.

    The site's ``q=PHI`` is a full-text search, so unrelated cases (e.g.
    ``355/Pdt.P/2026/PA.PLG`` or ``7843 K/PID.SUS/2026``) can appear.
    """
    return "phi" in (value or "").lower()


TOTAL_DATA_RE = re.compile(r"Ditemukan\s+([\d.,]+)\s+data", re.I)


def detect_total_data(soup: BeautifulSoup) -> int | None:
    """Parse the ``Ditemukan <N> data`` total from a listing page (None if absent)."""
    match = TOTAL_DATA_RE.search(soup.get_text(" ", strip=True))
    if not match:
        return None
    digits = re.sub(r"[^\d]", "", match.group(1))
    return int(digits) if digits else None


def detect_last_page(soup: BeautifulSoup) -> int:
    """Highest page number found in the paging widget (1 if none)."""
    last = 1
    for box in soup.select(".paging, .pagination"):
        for anchor in box.find_all("a", href=True):
            match = re.search(r"[?&]page=(\d+)", anchor["href"])
            if match:
                last = max(last, int(match.group(1)))
            elif anchor.get_text(strip=True).isdigit():
                last = max(last, int(anchor.get_text(strip=True)))
    return last


def looks_blocked(soup: BeautifulSoup) -> bool:
    """True when the response is an anti-bot/CAPTCHA page rather than the listing."""
    html = str(soup)
    if "spost" in html or "portfolio-meta" in html:
        return False
    return bool(re.search(r"bukan robot|are you human|not a robot|captcha|cloudflare", html, re.I))


# Party labels on the listing line, e.g. "Penggugat:<br />1.BUDI<br />2.ANI<br />Tergugat:<br />PT X".
PARTY_LABEL_RE = re.compile(r"(penggugat|tergugat|turut tergugat|pemohon|termohon)\s*:", re.I)
PARTY_FIELD = {
    "penggugat": "penggugat",
    "pemohon": "penggugat",
    "tergugat": "tergugat",
    "termohon": "tergugat",
}

# "NAME (Penggugat) VS NAME (Tergugat)" — the kasasi/MA listing style.
VS_RE = re.compile(r"\bvs\.?\b", re.I)
PAREN_LABEL_RE = re.compile(r"\(\s*(penggugat|tergugat|pemohon|termohon)\s*\)", re.I)


def _info_text(node: Any) -> str:
    """Text of a card info node, dropping the trailing view/download counters."""
    html = node.decode_contents()
    icon = html.find("icon-eye")
    if icon != -1:
        tag_start = html.rfind("<i", 0, icon)
        if tag_start != -1:
            html = html[:tag_start]
    return clean(BeautifulSoup(html, "html.parser").get_text(" ", strip=True))


def _parse_listing_vs(div: Any) -> Tuple[str, str]:
    """Parse ``Penggugat VS Tergugat`` (labels in parentheses) from a listing card."""
    nodes = [node for node in div.find_all("div") if VS_RE.search(node.get_text(" ", strip=True))]
    if not nodes:
        return "", ""
    text = _info_text(nodes[-1])
    if "\u2014" in text:
        text = text.split("\u2014", 1)[1]
    parts = VS_RE.split(text, maxsplit=1)
    if len(parts) != 2:
        return "", ""
    penggugat = clean(PAREN_LABEL_RE.sub("", parts[0])).strip(" -–—;,")
    tergugat = clean(PAREN_LABEL_RE.sub("", parts[1])).strip(" -–—;,")
    return penggugat, tergugat


def parse_listing_parties(div: Any) -> Tuple[str, str]:
    """Extract Penggugat/Tergugat from the listing info block.

    First tries the ``Label:<br />value<br />value...`` style (each value up to the
    next label; ``Turut Tergugat`` is a separate party and excluded). If that
    yields nothing, falls back to the ``Penggugat VS Tergugat`` style.
    """
    candidates = [node for node in div.find_all("div") if PARTY_LABEL_RE.search(node.get_text(" ", strip=True))]
    buckets: Dict[str, list] = {"penggugat": [], "tergugat": []}
    if candidates:
        current: str | None = None
        for chunk in re.split(r"<br\s*/?>", candidates[-1].decode_contents(), flags=re.I):
            if "icon-eye" in chunk or "icon-download" in chunk:
                break  # view/download counters follow the parties
            part = clean(BeautifulSoup(chunk, "html.parser").get_text(" ", strip=True))
            if not part:
                continue
            match = PARTY_LABEL_RE.search(part)
            if match:
                current = PARTY_FIELD.get(match.group(1).lower())
                rest = part[match.end():].strip(" :")
                if current and rest:
                    buckets[current].append(re.sub(r"^\d+\.\s*", "", rest))
            elif current:
                buckets[current].append(re.sub(r"^\d+\.\s*", "", part))
        parties = {key: "; ".join(value for value in values if value) for key, values in buckets.items()}
        if parties["penggugat"] or parties["tergugat"]:
            return parties["penggugat"], parties["tergugat"]
    return _parse_listing_vs(div)


def parse_listing_summary(div: Any) -> str:
    """Join every ``ul.nobottommargin li blockquote`` text on the listing card."""
    blocks = [clean(node.get_text(" ", strip=True)) for node in div.select("ul.nobottommargin li blockquote")]
    return "\n".join(block for block in blocks if block)


def parse_listing_item(div: Any) -> Dict[str, Any] | None:
    anchor = None
    for candidate in div.find_all("a", href=True):
        if "/direktori/putusan/" in candidate["href"]:
            anchor = candidate
            break
    anchor = anchor or div.find("a", href=True)
    if not anchor:
        return None
    text = clean(div.get_text(" "))
    register = re.search(r"Register\s*:?\s*([\d/\-]{8,10})", text, re.I)
    putus = re.search(r"Putus\s*:?\s*([\d/\-]{8,10})", text, re.I)
    status = STATUS_RE.search(text)
    penggugat, tergugat = parse_listing_parties(div)
    return {
        "judul": clean(anchor.get_text()),
        "url_detail": urljoin(BASE, anchor["href"]),
        "tgl_register_listing": parse_date(register.group(1)) if register else "",
        "tgl_putus_listing": parse_date(putus.group(1)) if putus else "",
        "Status_Putusan_Listing": clean(status.group(1)).title() if status else "",
        "penggugat_listing": penggugat,
        "tergugat_listing": tergugat,
        "ringkasan_listing": parse_listing_summary(div),
    }


def parse_detail(soup: BeautifulSoup) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    box = soup.select_one(".portfolio-meta")
    if not box:
        return out
    for row in box.select("table tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        label = clean(cells[0].get_text()).rstrip(":").lower()
        value = clean(cells[1].get_text(" "))
        key = DETAIL_MAP.get(label)
        if key and key not in out:
            out[key] = value
    for key in DATE_KEYS:
        if out.get(key):
            out[key] = parse_date(out[key])
    if out.get("Tahun", "").isdigit():
        out["Tahun"] = int(out["Tahun"])
    return out


def find_pdf_link(soup: BeautifulSoup) -> str:
    """Cari <li> 'Download PDF' -> ambil <a href>."""
    scopes = list(soup.select(".nobottommargin"))
    for comment in soup.find_all(string=lambda s: isinstance(s, Comment) and "Portfolio Single - Meta" in s):
        if comment.parent is not None:
            scopes.append(comment.parent)
    scopes.append(soup)
    for scope in scopes:
        for li in scope.find_all("li"):
            if li.find("li"):  # lewati li pembungkus
                continue
            if re.search(r"download\s*pdf", li.get_text(" "), re.I):
                anchor = li.find("a", href=True)
                if not anchor:  # kasus: teks di <li> ini, link di <li> berikutnya
                    nxt = li.find_next_sibling("li")
                    anchor = nxt.find("a", href=True) if nxt else None
                if anchor:
                    return urljoin(BASE, anchor["href"])
    return ""


def nomor_dari_judul(judul: str) -> str:
    match = NOMOR_RE.search(judul)
    return clean(match.group(1)) if match else ""


def split_pihak(judul: str, nomor: str = "") -> Tuple[str, str]:
    """Fallback Penggugat/Tergugat dari judul '... Nomor <no> <Penggugat> melawan <Tergugat>'."""
    nomor = nomor or nomor_dari_judul(judul)
    if nomor and nomor in judul:
        judul = judul.split(nomor, 1)[1]
    else:
        judul = re.sub(r"^Putusan\s+.*?Nomor\s+\S+\s*", "", judul, flags=re.I)
    match = re.search(r"(?:antara\s+)?(.+?)\s+(?:melawan|vs\.?|lawan)\s+(.+)", judul, re.I)
    return (clean(match.group(1)), clean(match.group(2))) if match else ("", "")


def anomaly_flags(putusan: Dict[str, Any]) -> list:
    flags = []
    register = putusan.get("Tanggal_Register")
    musyawarah = putusan.get("Tanggal_Musyawarah")
    dibacakan = putusan.get("Tanggal_Dibacakan")
    if register and musyawarah and musyawarah < register:
        flags.append("musyawarah<register")
    if dibacakan and dibacakan > date.today().isoformat():
        flags.append("dibacakan_di_masa_depan")
    if register and dibacakan and dibacakan < register:
        flags.append("putus<register")
    if putusan.get("Tahun") and register and str(putusan["Tahun"]) != register[:4]:
        flags.append("tahun!=tahun_register")
    return flags


def build_row(item: Dict[str, Any], detail: Dict[str, Any], link_file: str) -> Dict[str, Any]:
    putusan = {key: detail.get(key, "") for key in PUTUSAN_KEYS}
    putusan["Status_Putusan_Listing"] = item.get("Status_Putusan_Listing", "")
    putusan["Nomor_Perkara"] = putusan["Nomor_Perkara"] or nomor_dari_judul(item["judul"])
    # Listing labels are explicit ("Penggugat:"/"Tergugat:") and preferred; fall
    # back to the detail page table, then to the title ("A melawan B").
    putusan["Penggugat"] = item.get("penggugat_listing") or putusan["Penggugat"] or ""
    putusan["Tergugat"] = item.get("tergugat_listing") or putusan["Tergugat"] or ""
    if not putusan["Penggugat"] or not putusan["Tergugat"]:
        penggugat, tergugat = split_pihak(item["judul"], putusan["Nomor_Perkara"])
        putusan["Penggugat"] = putusan["Penggugat"] or penggugat
        putusan["Tergugat"] = putusan["Tergugat"] or tergugat
    putusan["Url_Detail"] = item["url_detail"]
    putusan["Anomali"] = anomaly_flags(putusan)

    # Typed fields must be None (not "") so the Pydantic model/Postgres date/int
    # columns validate and get the right type.
    if putusan.get("Tahun") in ("", None):
        putusan["Tahun"] = None
    for key in DATE_KEYS:
        if putusan.get(key) in ("", None):
            putusan[key] = None

    mulai = putusan["Tanggal_Register"] or item["tgl_register_listing"]
    putus = putusan["Tanggal_Dibacakan"] or item["tgl_putus_listing"]

    ringkasan = item.get("ringkasan_listing") or putusan["Abstrak"] or putusan["Kaidah"]
    if ringkasan in ("", "-"):
        ringkasan = clean(putusan["Catatan_Amar"])[:600]

    wilayah = putusan["Pengadilan"]
    if "mahkamah agung" in wilayah.lower():
        match = re.search(r"PHI\s+([A-Za-z .]+)", putusan["Kata_Kunci"])
        if match:
            wilayah = "PHI " + clean(match.group(1))

    lama = hari_kerja(mulai, putus)

    return {
        "nomor_perkara": putusan["Nomor_Perkara"],
        "jenis_perselisihan": jenis_perselisihan(" ".join(
            [item["judul"], putusan["Catatan_Amar"], putusan["Abstrak"], putusan["Kata_Kunci"]])),
        "tanggal_mulai_daftar": mulai or None,
        "tanggal_selesai_putus": putus or None,
        "lama_penyelesaian_hari_kerja": lama if lama != "" else None,
        "status_penyelesaian": status_penyelesaian(putusan["Catatan_Amar"], putusan["Amar"]),
        "nama_penggugat": putusan["Penggugat"],
        "nama_perusahaan_tergugat": putusan["Tergugat"],
        "sektor_industri": sektor_industri(putusan["Tergugat"], ringkasan),
        "wilayah_pengadilan": wilayah,
        "provinsi": provinsi_dari(wilayah, putusan["Pengadilan"], putusan["Kata_Kunci"], putusan["Nomor_Perkara"]),
        "tahun_periode": int((putus or mulai)[:4]) if (putus or mulai) else None,
        "ringkasan_pokok_sengketa": ringkasan,
        "putusan": putusan,
        "link_file": link_file,
        "minio_file": "",
    }


class Extractor(BaseExtractor):
    """Crawls the MA PHI putusan directory and yields ``Record``-shaped dicts."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        user_agent = _check_ascii("USER_AGENT", str(config.get("user_agent") or "").strip())
        cookie = _check_ascii("COOKIE", str(config.get("cookie") or "").strip())
        token = _check_ascii("TOKEN", str(config.get("token") or "").strip())
        # Passed per request so they win over HttpClient's default (Chrome) headers;
        # cf_clearance is bound to the exact User-Agent from the browser session.
        self._headers: Dict[str, str] = {}
        if user_agent:
            self._headers["User-Agent"] = user_agent
        if cookie:
            self._headers["Cookie"] = cookie
        if token:
            self.url = with_security_token(self.url or SEARCH_URL, token)

    def _get_soup(self, http: HttpClient, url: str) -> BeautifulSoup:
        return BeautifulSoup(http.get(url, headers=self._headers, timeout=60).text, "html.parser")

    def _fetch_soup(self, url: str) -> BeautifulSoup:
        return self._get_soup(self.http, url)

    def _page_rows(self, page: int, listing: BeautifulSoup | None = None) -> List[Dict[str, Any]]:
        """Fetch one listing page and its detail pages; safe to run in a worker thread.

        Each call uses its own ``HttpClient`` (and therefore its own ``requests``
        session) because ``requests.Session`` is not thread-safe.
        """
        http = HttpClient(default_headers=self._headers)
        soup = listing or self._get_soup(http, page_url(self.url or SEARCH_URL, page))
        cards = soup.select("div.spost")
        if not cards:
            if looks_blocked(soup):
                raise SourceUnavailable(
                    "Anti-bot/Cloudflare verification page returned. Refresh COOKIE, TOKEN and "
                    "USER_AGENT in scripts/.env.dev with values from a browser session that "
                    "already passed the check."
                )
            return []

        # Keep only PHI cases; a page of unrelated hits must not stop the crawl.
        items = [
            item
            for item in (parse_listing_item(node) for node in cards)
            if item and is_phi_case(item["judul"])
        ]

        rows: List[Dict[str, Any]] = []
        for item in items:
            time.sleep(REQUEST_DELAY)
            try:
                detail_soup = self._get_soup(http, item["url_detail"])
            except Exception:  # noqa: BLE001 - keep going with partial detail
                detail_soup = None
            detail = parse_detail(detail_soup) if detail_soup else {}
            link_file = find_pdf_link(detail_soup) if detail_soup else ""
            row = build_row(item, detail, link_file)
            if is_phi_case(row.get("nomor_perkara")):
                rows.append(row)
        return rows

    def extract(self) -> Iterator[Dict[str, Any]]:
        url = self.url or SEARCH_URL

        # Page 1 is fetched up front to discover the total row count, then its
        # listing soup is reused (no extra request).
        discovery = HttpClient(default_headers=self._headers)
        first = self._get_soup(discovery, page_url(url, 1))
        if not first.select("div.spost") and looks_blocked(first):
            raise SourceUnavailable(
                "Anti-bot/Cloudflare verification page returned. Refresh COOKIE, TOKEN and "
                "USER_AGENT in scripts/.env.dev with values from a browser session that "
                "already passed the check."
            )

        total = detect_total_data(first)
        page_count = detect_last_page(first)
        if total:
            page_count = max(page_count, math.ceil(total / ROWS_PER_PAGE))
        if MAX_PAGES is not None:
            page_count = min(page_count, MAX_PAGES)

        yield from self._page_rows(1, first)

        # Remaining pages are crawled concurrently (CONCURRENCY workers).
        if page_count > 1:
            with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
                futures = [executor.submit(self._page_rows, page) for page in range(2, page_count + 1)]
                for future in as_completed(futures):
                    yield from future.result()
