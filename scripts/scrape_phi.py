#!/usr/bin/env python3
"""
Scraper Direktori Putusan MA (putusan3.mahkamahagung.go.id) - perkara PHI.

Alur:
  1. Buka halaman search -> iterasi tiap div.spost (listing)
  2. Buka link <a href> di tiap spost -> parse div.portfolio-meta > table (detail)
     + cari link "Download PDF" (area .nobottommargin / komentar "Portfolio Single - Meta")
  3. Lanjut ke halaman berikutnya (class paging) sampai habis / sampai batas page

Output mengikuti data dictionary utama; seluruh field detail (dictionary "putusan")
disimpan di kolom `putusan` (JSON).

Contoh:
  python scrape_phi.py                          # semua page -> CSV
  python scrape_phi.py --max-pages 3
  python scrape_phi.py --start-page 5 --end-page 10
  python scrape_phi.py --output putusan_phi.jsonl   # JSON Lines (putusan = objek bersarang)
  python scrape_phi.py --resume

Dependensi: pip install requests beautifulsoup4 numpy
"""
import argparse
import csv
import json
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

import numpy as np
import requests
from bs4 import BeautifulSoup, Comment

BASE = "https://putusan3.mahkamahagung.go.id/"
SEARCH_URL = BASE + "search.html"

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

COLUMNS = [
    "nomor_perkara", "jenis_perselisihan", "tanggal_mulai_daftar", "tanggal_selesai_putus",
    "lama_penyelesaian_hari_kerja", "status_penyelesaian", "nama_penggugat",
    "nama_perusahaan_tergugat", "sektor_industri", "wilayah_pengadilan", "provinsi",
    "tahun_periode", "ringkasan_pokok_sengketa", "putusan", "link_file", "minio_file",
]

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


# --------------------------------------------------------------------------- utils
def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def parse_date(text):
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


def hari_kerja(start_iso, end_iso):
    """Hari kerja Senin-Jumat; libur nasional TIDAK dihitung."""
    if not start_iso or not end_iso:
        return ""
    s, e = date.fromisoformat(start_iso), date.fromisoformat(end_iso)
    if e < s:
        return ""
    return int(np.busday_count(s, e))


def jenis_perselisihan(text):
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


def status_penyelesaian(catatan_amar, amar=""):
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


def sektor_industri(nama_tergugat, ringkasan=""):
    for text in (nama_tergugat or "", ringkasan or ""):
        t = text.lower()
        for label, pat in SEKTOR:
            if re.search(pat, t):
                return label
    return ""


def provinsi_dari(*sources):
    text = " ".join(s.lower() for s in sources if s)
    for key in sorted(PROVINSI, key=len, reverse=True):
        if re.search(r"(?<![a-z])" + re.escape(key), text):
            return PROVINSI[key]
    return ""


def load_dotenv(path):
    """Baca file .env sederhana (KEY=VALUE). Tidak menimpa variabel yang sudah ada di environment."""
    import os
    f = Path(path)
    if not f.exists():
        return False
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, _, val = line.partition("=")
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        os.environ.setdefault(key.strip(), val)
    return True


def normalize_cookie(raw):
    """Terima 'a=1; b=2' atau hasil paste DevTools (satu cookie per baris: nama<TAB>nilai)."""
    raw = (raw or "").strip()
    if not raw:
        return ""
    if "\n" in raw or "\t" in raw:
        pairs = []
        for line in raw.splitlines():
            parts = re.split(r"\t+|\s{2,}", line.strip(), maxsplit=1)
            if len(parts) == 2:
                pairs.append(f"{parts[0]}={parts[1].strip().strip(chr(34))}")
        return "; ".join(pairs)
    return raw


def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0 Safari/537.36",
        "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    })
    return s


def fetch(session, url, retries=4, timeout=40, backoff=3.0):
    if hasattr(session, "get_soup"):  # mode --browser
        return session.get_soup(url)
    for i in range(1, retries + 1):
        try:
            r = session.get(url, timeout=timeout)
            if r.status_code == 200:
                return BeautifulSoup(r.text, "html.parser")
            print(f"  [warn] HTTP {r.status_code} {url} ({i}/{retries})", file=sys.stderr)
        except requests.RequestException as e:
            print(f"  [warn] {e.__class__.__name__} {url} ({i}/{retries})", file=sys.stderr)
        time.sleep(backoff * i)
    return None


class BrowserFetcher:
    """Human-in-the-loop: browser tampil di layar; Anda sendiri yang mencentang
    'saya bukan robot' dan menekan Cari. Script TIDAK membuka ulang URL hasil search
    (token bisa sekali pakai); ia membaca halaman yang sudah tampil lalu pindah page
    dengan mengklik link paging. Halaman detail dibuka di tab kedua."""

    def __init__(self, start_url, profile_dir, channel=None, engine="chromium"):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            sys.exit("Install dulu: pip install playwright && playwright install chromium firefox")
        self._pw = sync_playwright().start()
        kw = {"headless": False}
        if channel and engine == "chromium":  # contoh: "chrome" = Google Chrome terpasang
            kw["channel"] = channel
        self.ctx = getattr(self._pw, engine).launch_persistent_context(profile_dir, **kw)
        self.page = self.ctx.pages[0] if self.ctx.pages else self.ctx.new_page()
        self.detail_page = self.ctx.new_page()
        self.page.bring_to_front()
        self.page.goto(SEARCH_URL)
        while True:
            input(">> Di TAB PERTAMA: isi pencarian 'PHI', centang 'saya bukan robot', klik Cari "
                  "sampai daftar putusan tampil.\n   Setelah itu tekan ENTER di sini... ")
            if "spost" in self.page.content():
                break
            print(">> Daftar putusan belum terlihat di tab pertama. Pastikan hasil pencarian tampil, "
                  "lalu ENTER lagi.")
        self.search_url = self.page.url

    @staticmethod
    def _blocked(status, html):
        ok = "spost" in html or "portfolio-meta" in html
        return bool((status in (403, 429) or re.search(r"bukan robot|captcha|not a robot", html, re.I)) and not ok)

    def _cur_page(self):
        m = re.search(r"[?&]page=(\d+)", self.page.url)
        return int(m.group(1)) if m else 1

    def _checked_soup(self, page, status=200):
        for _ in range(3):
            html = page.content()
            if not self._blocked(status, html):
                return BeautifulSoup(html, "html.parser")
            input(">> Verifikasi/blokir terdeteksi di tab yang sedang diproses. Selesaikan di browser, "
                  "lalu tekan ENTER untuk mencoba lagi... ")
            status = 200
        return None

    def _click_paging(self, target):
        links = self.page.locator(".paging a, .pagination a")
        for i in range(links.count()):
            el = links.nth(i)
            href = el.get_attribute("href") or ""
            m = re.search(r"[?&]page=(\d+)", href)
            label = (el.inner_text() or "").strip()
            if (m and int(m.group(1)) == target) or label == str(target):
                el.click()
                self.page.wait_for_load_state("domcontentloaded")
                time.sleep(1.0)
                return True
        return False

    def open_page(self, n):
        """Tampilkan listing page n (mengklik link paging, melangkah satu-satu bila perlu)."""
        for _ in range(500):
            cur = self._cur_page()
            if cur == n:
                return self._checked_soup(self.page)
            if n < cur:
                print("  [warn] tidak bisa mundur ke page sebelumnya di mode browser.", file=sys.stderr)
                return None
            if not (self._click_paging(n) or self._click_paging(cur + 1)):
                return None
        return None

    def get_soup(self, url):
        """Halaman detail: dibuka di tab kedua."""
        resp = self.detail_page.goto(url, wait_until="domcontentloaded")
        return self._checked_soup(self.detail_page, resp.status if resp else 0)

    def close(self):
        self.ctx.close()
        self._pw.stop()


def page_url(base_url, page):
    u = urlparse(base_url)
    q = parse_qs(u.query, keep_blank_values=True)
    if page <= 1:
        q.pop("page", None)
    else:
        q["page"] = [str(page)]
    return urlunparse(u._replace(query=urlencode(q, doseq=True)))


def detect_last_page(soup):
    last = 1
    for box in soup.select(".paging, .pagination"):
        for a in box.find_all("a", href=True):
            m = re.search(r"[?&]page=(\d+)", a["href"])
            if m:
                last = max(last, int(m.group(1)))
            elif a.get_text(strip=True).isdigit():
                last = max(last, int(a.get_text(strip=True)))
    return last


# --------------------------------------------------------------------------- parsing
STATUS_RE = re.compile(r"(belum berkekuatan hukum tetap|berkekuatan hukum tetap|inkracht)", re.I)


def parse_listing_item(div):
    a = None
    for cand in div.find_all("a", href=True):
        if "/direktori/putusan/" in cand["href"]:
            a = cand
            break
    a = a or div.find("a", href=True)
    if not a:
        return None
    text = clean(div.get_text(" "))
    reg = re.search(r"Register\s*:?\s*([\d/\-]{8,10})", text, re.I)
    put = re.search(r"Putus\s*:?\s*([\d/\-]{8,10})", text, re.I)
    st = STATUS_RE.search(text)
    return {
        "judul": clean(a.get_text()),
        "url_detail": urljoin(BASE, a["href"]),
        "tgl_register_listing": parse_date(reg.group(1)) if reg else "",
        "tgl_putus_listing": parse_date(put.group(1)) if put else "",
        "Status_Putusan_Listing": clean(st.group(1)).title() if st else "",
    }


def parse_detail(soup):
    out = {}
    box = soup.select_one(".portfolio-meta")
    if not box:
        return out
    for tr in box.select("table tr"):
        cells = tr.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        label = clean(cells[0].get_text()).rstrip(":").lower()
        value = clean(cells[1].get_text(" "))
        key = DETAIL_MAP.get(label)
        if key and key not in out:
            out[key] = value
    for k in DATE_KEYS:
        if out.get(k):
            out[k] = parse_date(out[k])
    if out.get("Tahun", "").isdigit():
        out["Tahun"] = int(out["Tahun"])
    return out


def find_pdf_link(soup):
    """Cari <li> 'Download PDF' -> ambil <a href>.
    Scope: .nobottommargin, parent dari komentar 'Portfolio Single - Meta', lalu seluruh halaman."""
    scopes = list(soup.select(".nobottommargin"))
    for c in soup.find_all(string=lambda s: isinstance(s, Comment) and "Portfolio Single - Meta" in s):
        if c.parent is not None:
            scopes.append(c.parent)
    scopes.append(soup)
    for scope in scopes:
        for li in scope.find_all("li"):
            if li.find("li"):  # lewati li pembungkus
                continue
            if re.search(r"download\s*pdf", li.get_text(" "), re.I):
                a = li.find("a", href=True)
                if not a:  # kasus: teks di <li> ini, link di <li> berikutnya
                    nxt = li.find_next_sibling("li")
                    a = nxt.find("a", href=True) if nxt else None
                if a:
                    return urljoin(BASE, a["href"])
    return ""


NOMOR_RE = re.compile(r"Nomor\s+(\d+\s?K?/Pdt\.Sus[\w\-./]*(?:\s+PN\s+[A-Za-z.]+)?)", re.I)


def nomor_dari_judul(judul):
    m = NOMOR_RE.search(judul)
    return clean(m.group(1)) if m else ""


def split_pihak(judul, nomor=""):
    """Fallback Penggugat/Tergugat dari judul '... Nomor <no> <Penggugat> melawan <Tergugat>'."""
    nomor = nomor or nomor_dari_judul(judul)
    if nomor and nomor in judul:
        judul = judul.split(nomor, 1)[1]
    else:
        judul = re.sub(r"^Putusan\s+.*?Nomor\s+\S+\s*", "", judul, flags=re.I)
    m = re.search(r"(?:antara\s+)?(.+?)\s+(?:melawan|vs\.?|lawan)\s+(.+)", judul, re.I)
    return (clean(m.group(1)), clean(m.group(2))) if m else ("", "")


def anomaly_flags(p):
    f = []
    reg, mus, dib = p.get("Tanggal_Register"), p.get("Tanggal_Musyawarah"), p.get("Tanggal_Dibacakan")
    if reg and mus and mus < reg:
        f.append("musyawarah<register")
    if dib and dib > date.today().isoformat():
        f.append("dibacakan_di_masa_depan")
    if reg and dib and dib < reg:
        f.append("putus<register")
    if p.get("Tahun") and reg and str(p["Tahun"]) != reg[:4]:
        f.append("tahun!=tahun_register")
    return f


# --------------------------------------------------------------------------- build
def build_row(item, detail, link_file):
    putusan = {k: detail.get(k, "") for k in PUTUSAN_KEYS}
    putusan["Status_Putusan_Listing"] = item.get("Status_Putusan_Listing", "")
    putusan["Nomor_Perkara"] = putusan["Nomor_Perkara"] or nomor_dari_judul(item["judul"])
    if not putusan["Penggugat"] or not putusan["Tergugat"]:
        p, t = split_pihak(item["judul"], putusan["Nomor_Perkara"])
        putusan["Penggugat"] = putusan["Penggugat"] or p
        putusan["Tergugat"] = putusan["Tergugat"] or t
    putusan["Url_Detail"] = item["url_detail"]
    putusan["Anomali"] = anomaly_flags(putusan)

    mulai = putusan["Tanggal_Register"] or item["tgl_register_listing"]
    putus = putusan["Tanggal_Dibacakan"] or item["tgl_putus_listing"]

    ringkasan = putusan["Abstrak"] or putusan["Kaidah"]
    if ringkasan in ("", "-"):
        ringkasan = clean(putusan["Catatan_Amar"])[:600]

    # wilayah: untuk kasasi (MA) pakai "PHI <kota>" dari Kata_Kunci bila ada
    wilayah = putusan["Pengadilan"]
    if "mahkamah agung" in wilayah.lower():
        m = re.search(r"PHI\s+([A-Za-z .]+)", putusan["Kata_Kunci"])
        if m:
            wilayah = "PHI " + clean(m.group(1))

    return {
        "nomor_perkara": putusan["Nomor_Perkara"],
        "jenis_perselisihan": jenis_perselisihan(" ".join(
            [item["judul"], putusan["Catatan_Amar"], putusan["Abstrak"], putusan["Kata_Kunci"]])),
        "tanggal_mulai_daftar": mulai,
        "tanggal_selesai_putus": putus,
        "lama_penyelesaian_hari_kerja": hari_kerja(mulai, putus),
        "status_penyelesaian": status_penyelesaian(putusan["Catatan_Amar"], putusan["Amar"]),
        "nama_penggugat": putusan["Penggugat"],
        "nama_perusahaan_tergugat": putusan["Tergugat"],
        "sektor_industri": sektor_industri(putusan["Tergugat"], ringkasan),
        "wilayah_pengadilan": wilayah,
        "provinsi": provinsi_dari(wilayah, putusan["Pengadilan"], putusan["Kata_Kunci"], putusan["Nomor_Perkara"]),
        "tahun_periode": int((putus or mulai)[:4]) if (putus or mulai) else "",
        "ringkasan_pokok_sengketa": ringkasan,
        "putusan": putusan,
        "link_file": link_file,
        "minio_file": "",
    }


def serialize(row, jsonl):
    if jsonl:
        return row
    r = dict(row)
    r["putusan"] = json.dumps(row["putusan"], ensure_ascii=False)
    return r


def load_done(path, jsonl):
    done = set()
    if not path.exists():
        return done
    if jsonl:
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(json.loads(line)["putusan"]["Url_Detail"])
                except (ValueError, KeyError):
                    pass
    else:
        with path.open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                try:
                    done.add(json.loads(r["putusan"])["Url_Detail"])
                except (ValueError, KeyError):
                    pass
    return done


def main():
    ap = argparse.ArgumentParser(description="Scraper putusan PHI - putusan3.mahkamahagung.go.id")
    ap.add_argument("--url", default=None, help="URL search awal (default: PHI_SEARCH_URL dari .env)")
    ap.add_argument("--env-file", default=".env", help="file .env (PHI_SEARCH_URL, PHI_COOKIE, PHI_USER_AGENT)")
    ap.add_argument("--start-page", type=int, default=1)
    ap.add_argument("--end-page", type=int, default=None, help="page akhir (default: sampai habis)")
    ap.add_argument("--max-pages", type=int, default=None, help="jumlah page maksimum yang diambil")
    ap.add_argument("--delay", type=float, default=1.5, help="jeda antar request (detik)")
    ap.add_argument("--output", default="putusan_phi.csv", help=".csv atau .jsonl")
    ap.add_argument("--resume", action="store_true", help="append & skip perkara yang sudah ada")
    ap.add_argument("--html-dir", default=None,
                    help="parse file HTML halaman detail yang Anda simpan manual (tanpa request ke situs)")
    ap.add_argument("--browser", action="store_true",
                    help="buka browser; Anda centang 'bukan robot' manual, script lanjut otomatis")
    ap.add_argument("--browser-engine", choices=["chromium", "firefox"], default="chromium",
                    help="engine browser untuk mode --browser (default chromium)")
    ap.add_argument("--browser-channel", default=None,
                    help="mis. 'chrome' untuk memakai Google Chrome yang terpasang (mode --browser)")
    ap.add_argument("--profile-dir", default=".browser_profile", help="folder profil browser (mode --browser)")
    ap.add_argument("--user-agent", default=None,
                    help="User-Agent browser Anda (WAJIB sama dengan yang dipakai saat lolos Cloudflare, utk --cookie)")
    ap.add_argument("--cookie", default=None,
                    help="string Cookie dari browser Anda yang sudah lolos verifikasi (mode tanpa browser)")
    args = ap.parse_args()

    import os
    if load_dotenv(args.env_file):
        print(f"Memuat konfigurasi dari {args.env_file}")
    args.url = args.url or os.environ.get("PHI_SEARCH_URL") or (SEARCH_URL + "?q=PHI&security_token=")
    args.cookie = args.cookie or os.environ.get("PHI_COOKIE")
    args.user_agent = args.user_agent or os.environ.get("PHI_USER_AGENT")
    if not (args.browser or args.html_dir) and (not args.cookie or "security_token=" not in args.url
                                                or args.url.rstrip().endswith("security_token=")):
        print("[warn] PHI_SEARCH_URL (dengan token terisi) / PHI_COOKIE belum diset; "
              "kemungkinan besar akan 403.", file=sys.stderr)

    out_path = Path(args.output)
    jsonl = out_path.suffix.lower() == ".jsonl"
    done = load_done(out_path, jsonl) if args.resume else set()
    if done:
        print(f"Resume: {len(done)} perkara sudah ada, dilewati.")
    append = args.resume and out_path.exists()

    if args.html_dir:
        files = sorted(Path(args.html_dir).glob("*.htm*"))
        if not files:
            sys.exit(f"Tidak ada file .html di {args.html_dir}")
        n_rows = 0
        with out_path.open("a" if append else "w", newline="", encoding="utf-8" if jsonl else "utf-8-sig") as f:
            writer = None
            if not jsonl:
                writer = csv.DictWriter(f, fieldnames=COLUMNS)
                if not append:
                    writer.writeheader()
            for fp in files:
                soup = BeautifulSoup(fp.read_text(encoding="utf-8", errors="ignore"), "html.parser")
                canon = soup.select_one('link[rel="canonical"]') or soup.select_one('meta[property="og:url"]')
                url_detail = (canon.get("href") or canon.get("content")) if canon else fp.resolve().as_uri()
                h = soup.select_one("h1, h2") or soup.title
                item = {"judul": clean(h.get_text()) if h else fp.stem, "url_detail": url_detail,
                        "tgl_register_listing": "", "tgl_putus_listing": "", "Status_Putusan_Listing": ""}
                if url_detail in done:
                    continue
                row = build_row(item, parse_detail(soup), find_pdf_link(soup))
                if jsonl:
                    f.write(json.dumps(serialize(row, True), ensure_ascii=False) + "\n")
                else:
                    writer.writerow(serialize(row, False))
                n_rows += 1
                print(f"  + {fp.name}: {row['nomor_perkara'][:60]} | {row['status_penyelesaian'] or '-'} | pdf={'ya' if row['link_file'] else 'tidak'}")
        print(f"\nSelesai: {n_rows} baris dari {len(files)} file -> {out_path}")
        return

    if args.browser:
        session = BrowserFetcher(args.url, args.profile_dir, args.browser_channel, args.browser_engine)
        print("Mode browser: listing dibaca dari tab pertama, paging lewat klik link.")
    else:
        session = make_session()
        if args.user_agent:
            session.headers["User-Agent"] = args.user_agent
        if args.cookie:
            session.headers["Cookie"] = normalize_cookie(args.cookie)
    n_pages = n_rows = 0
    page = args.start_page
    last_page = args.end_page

    with out_path.open("a" if append else "w", newline="", encoding="utf-8" if jsonl else "utf-8-sig") as f:
        writer = None
        if not jsonl:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            if not append:
                writer.writeheader()

        while True:
            if last_page and page > last_page:
                break
            if args.max_pages and n_pages >= args.max_pages:
                break

            if args.browser:
                print(f"[page {page}] (browser)")
                soup = session.open_page(page)
            else:
                url = page_url(args.url, page)
                print(f"[page {page}] {url}")
                soup = fetch(session, url)
            if soup is None:
                print("  gagal mengambil page, berhenti.", file=sys.stderr)
                break

            items = [i for i in (parse_listing_item(d) for d in soup.select("div.spost")) if i]
            if not items:
                print("  tidak ada div.spost -> selesai.")
                break

            if args.end_page is None and last_page is None:
                lp = detect_last_page(soup)
                if lp > 1:
                    print(f"  page terakhir terdeteksi dari paging: {lp}")
                    last_page = lp

            for it in items:
                if it["url_detail"] in done:
                    continue
                time.sleep(args.delay)
                dsoup = fetch(session, it["url_detail"])
                if dsoup is None:
                    print(f"  gagal detail: {it['url_detail']}", file=sys.stderr)
                    detail, link = {}, ""
                else:
                    detail, link = parse_detail(dsoup), find_pdf_link(dsoup)
                row = build_row(it, detail, link)
                if jsonl:
                    f.write(json.dumps(serialize(row, True), ensure_ascii=False) + "\n")
                else:
                    writer.writerow(serialize(row, False))
                f.flush()
                n_rows += 1
                print(f"  + {row['nomor_perkara'][:70]} | {row['status_penyelesaian'] or '-'} | pdf={'ya' if link else 'tidak'}")

            n_pages += 1
            page += 1
            time.sleep(args.delay)

    if args.browser:
        session.close()
    print(f"\nSelesai: {n_pages} page, {n_rows} baris baru -> {out_path}")


if __name__ == "__main__":
    main()