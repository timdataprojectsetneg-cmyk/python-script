#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import json
import time
import logging
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("jdih_scraper_bpk")

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
}


def setup_logging(level: str = "INFO") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(lvl)
    h = logging.StreamHandler(stream=sys.stderr)
    h.setLevel(lvl)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
    logger.handlers = [h]


# ---------------- SQL helpers ----------------
def sql_quote(s: Optional[str]) -> str:
    """Return SQL single-quoted string or NULL."""
    if s is None:
        return "NULL"
    s = str(s)
    return "'" + s.replace("'", "''") + "'"


def sql_jsonb(obj: Any) -> str:
    """Return ::jsonb literal or '{}'::jsonb."""
    if obj is None:
        obj = {}
    # compact JSON to reduce size
    j = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return sql_quote(j) + "::jsonb"


def sql_text_array(arr: Any) -> str:
    """Return Postgres text[] literal."""
    if not arr:
        return "ARRAY[]::text[]"
    if not isinstance(arr, list):
        arr = [str(arr)]
    items = []
    for x in arr:
        if x is None:
            continue
        # escape quotes/backslashes
        v = str(x).replace("\\", "\\\\").replace('"', '\\"')
        items.append(f'"{v}"')
    if not items:
        return "ARRAY[]::text[]"
    return "ARRAY[" + ",".join(items) + "]::text[]"


# ---------------- scraping utils ----------------
def detect_max_pages(soup: BeautifulSoup) -> int:
    max_page = 1
    try:
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if "?p=" in href or "&p=" in href:
                try:
                    page_param = href.split("&p=")[1] if "&p=" in href else href.split("?p=")[1]
                    page_num_str = page_param.split("&")[0].split("#")[0]
                    max_page = max(max_page, int(page_num_str))
                except Exception:
                    continue

        for text in soup.find_all(string=lambda t: t and ("of" in t.lower() or "dari" in t.lower())):
            m = re.search(r"(\d+)\s*(?:of|dari)\s*(\d+)", str(text), re.IGNORECASE)
            if m:
                max_page = max(max_page, int(m.group(2)))
    except Exception:
        return 1
    return max_page


def convert_date_format(date_str: str) -> str:
    if not date_str:
        return ""
    months = {
        "januari": "01", "februari": "02", "maret": "03", "april": "04",
        "mei": "05", "juni": "06", "juli": "07", "agustus": "08",
        "september": "09", "oktober": "10", "november": "11", "desember": "12"
    }
    try:
        parts = date_str.strip().split()
        if len(parts) >= 3:
            day = parts[0].zfill(2)
            month = months.get(parts[1].lower())
            year = parts[2]
            if month:
                return f"{year}-{month}-{day}"
    except Exception:
        pass
    return date_str


def parse_berlaku_text(berlaku_text: str) -> Optional[datetime]:
    if not berlaku_text:
        return None
    t = berlaku_text.lower()
    m = re.search(r"berlaku\s+mulai\s+(\d+)\s+hari\s+yang\s+lalu", t)
    if m:
        return datetime.now() - timedelta(days=int(m.group(1)))
    m = re.search(r"berlaku\s+mulai\s+(\d+)\s+minggu\s+yang\s+lalu", t)
    if m:
        return datetime.now() - timedelta(weeks=int(m.group(1)))
    m = re.search(r"berlaku\s+mulai\s+(\d+)\s+bulan\s+yang\s+lalu", t)
    if m:
        return datetime.now() - timedelta(days=int(m.group(1)) * 30)
    return None


def is_within_date_range(berlaku_text: str, max_days_ago: int = 30) -> bool:
    if not berlaku_text:
        return True
    dt = parse_berlaku_text(berlaku_text)
    if not dt:
        return True
    return dt >= (datetime.now() - timedelta(days=max_days_ago))


def parse_materi_pokok_from_soup(soup: BeautifulSoup) -> Optional[str]:
    for heading in soup.find_all("h4", class_="text-primary"):
        if "MATERI POKOK" in heading.get_text(strip=True).upper():
            card_body = heading.find_parent("div", class_="card-body")
            if card_body:
                p = card_body.find("p")
                if p:
                    t = p.get_text(strip=True)
                    if t:
                        return t
    for card in soup.find_all("div", class_="card"):
        h4 = card.find("h4", class_="text-primary")
        if h4 and "MATERI POKOK" in h4.get_text(strip=True).upper():
            p = card.find("p")
            if p:
                t = p.get_text(strip=True)
                if t:
                    return t
    for heading in soup.find_all(["h4", "h5", "h6"]):
        if "MATERI POKOK" in heading.get_text(strip=True).upper():
            p = heading.find_next("p")
            if p:
                t = p.get_text(strip=True)
                if t and len(t) > 20:
                    return t
    return None


def parse_abstrak_peraturan_from_soup(soup: BeautifulSoup) -> Optional[Dict[str, List[str]]]:
    abstrak_points: List[str] = []

    dash_ul = soup.find("ul", class_="dash")
    if dash_ul:
        for li in dash_ul.find_all("li", recursive=False):
            text = li.get_text(strip=True)
            if text:
                abstrak_points.append(text)

    if not abstrak_points:
        abstrak_modal = soup.find("div", {"id": "modal-content"})
        if abstrak_modal:
            lis = abstrak_modal.find_all("li")
            if lis:
                for li in lis:
                    text = li.get_text(strip=True)
                    if text:
                        abstrak_points.append(text)
            else:
                abstrak_points.append(abstrak_modal.get_text(strip=True))

    if not abstrak_points:
        for heading in soup.find_all(["h4", "h5", "h6", "td"]):
            if "ABSTRAK" in heading.get_text(strip=True).upper():
                parent = heading.find_parent(["div", "td"])
                if parent:
                    lis = parent.find_all("li")
                    if lis:
                        for li in lis:
                            text = li.get_text(strip=True)
                            if text:
                                abstrak_points.append(text)
                    else:
                        abstrak_points.append(parent.get_text(strip=True))
                break

    if not abstrak_points:
        return None

    regulation_patterns = [
        ("UNDANG-UNDANG DASAR", "UUD"),
        ("UNDANG-UNDANG", "UU"),
        ("UU", "UU"),
        ("PERATURAN PEMERINTAH PENGGANTI UNDANG-UNDANG", "PERPPU"),
        ("PERPPU", "PERPPU"),
        ("PERATURAN PEMERINTAH", "PP"),
        ("PP", "PP"),
        ("PERATURAN PRESIDEN", "PERPRES"),
        ("PERPRES", "PERPRES"),
        ("PERATURAN MENTERI", "PERMEN"),
        ("PERMEN", "PERMEN"),
        ("KEPUTUSAN PRESIDEN", "KEPRES"),
        ("KEPRES", "KEPRES"),
        ("KEPPRES", "KEPRES"),
        ("INSTRUKSI PRESIDEN", "INPRES"),
        ("INPRES", "INPRES"),
        ("PERATURAN DAERAH", "PERDA"),
        ("PERDA", "PERDA"),
    ]

    peraturan_dict: Dict[str, List[str]] = {}
    for abstrak_text in abstrak_points:
        for pattern_text, normalized_type in regulation_patterns:
            patterns = [
                rf"{pattern_text}\s+(?:Nomor|No\.?|Nummer)\s+(\d+)\s+(?:Tahun|Thn\.?)\s+(\d{{4}})",
                rf"{pattern_text}\s+(\d+)/(\d{{4}})",
                rf"{pattern_text}\s+(\d+)\s+Tahun\s+(\d{{4}})",
            ]
            for pat in patterns:
                for m in re.finditer(pat, abstrak_text, re.IGNORECASE):
                    ref = f"{normalized_type} {m.group(1)}/{m.group(2)}"
                    peraturan_dict.setdefault(normalized_type, [])
                    if ref not in peraturan_dict[normalized_type]:
                        peraturan_dict[normalized_type].append(ref)

    for k in peraturan_dict:
        peraturan_dict[k] = sorted(list(set(peraturan_dict[k])))

    return peraturan_dict or None


# ---------------- core scraping ----------------
def scrape_regulations_by_type(
    type_url: str,
    type_name: str,
    year_filter: Optional[List[int]] = None,
    max_days_ago: int = 30,
    sleep_seconds: float = 2.0,
) -> List[Dict[str, Any]]:
    all_links: List[Dict[str, Any]] = []
    page = 1
    max_pages = None

    logger.info("Scraping links for type: %s", type_name)

    while True:
        separator = "&" if "?" in type_url else "?"
        url = f"{type_url}{separator}p={page}"
        if year_filter:
            for y in year_filter:
                url += f"&tahun={y}"

        try:
            r = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "html.parser")

            if max_pages is None:
                max_pages = detect_max_pages(soup)
                logger.info("Detected total pages: %s", max_pages)

            if page > (max_pages or 1):
                break

            seen = set()
            page_links: List[Dict[str, Any]] = []

            for card in soup.find_all("div", class_="card"):
                berlaku_span = card.find("span", class_="text-muted")
                if berlaku_span:
                    berlaku_text = berlaku_span.get_text(strip=True)
                    if not is_within_date_range(berlaku_text, max_days_ago=max_days_ago):
                        continue

                main_link = None
                col_lg_10 = card.find("div", class_=lambda x: x and "col-lg-10" in x)
                if col_lg_10:
                    main_link = col_lg_10.find("a", class_=lambda x: x and "fw-bold" in x, href=True)
                if not main_link:
                    main_link = card.find("a", class_=lambda x: x and "fw-bold" in x, href=True)
                if not main_link:
                    for a in card.find_all("a", href=True):
                        href = a.get("href")
                        if href and "/Details/" in href:
                            main_link = a
                            break
                if not main_link:
                    continue

                href = main_link.get("href")
                if not (href and "/Details/" in href):
                    continue

                full_url = href if href.startswith("http") else f"https://peraturan.bpk.go.id{href}"
                if full_url in seen:
                    continue
                seen.add(full_url)

                title = " ".join(main_link.get_text(strip=True).split())
                page_links.append({"url": full_url, "title": title, "type": type_name, "page": page})

            if not page_links:
                break

            all_links.extend(page_links)
            logger.info("Page %s: %s links", page, len(page_links))

            page += 1
            time.sleep(sleep_seconds)

        except Exception as e:
            logger.error("Error page %s: %s", page, e, exc_info=True)
            break

    return all_links


def scrape_regulation_details(detail_url: str) -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(detail_url, headers=DEFAULT_HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")

        source_download_url = None
        a = soup.select_one("a.download-file[href]")
        if a and a.get("href"):
            href = a.get("href")
            source_download_url = href if href.startswith("http") else f"https://peraturan.bpk.go.id{href}"

        details: Dict[str, Any] = {
            "id_source": detail_url.split("/")[-2] if "/" in detail_url else "",
            "source_url": detail_url,
            "source_url_download": source_download_url,
            "jenis": "",
            "instansi": "",
            "nomor": "",
            "tahun": "",
            "tentang": "",
            "status": {},
            "tanggal_ditetapkan": "",
            "tanggal_diundangkan": "",
            "tanggal_berlaku": "",
            "nama_file": "",
            "lampiran": [],
            "description": "",
            "peraturan_terkait": {},
        }

        main_container = soup.find("div", class_="container fs-6") or soup
        metadata_sections = main_container.find_all(
            "div",
            class_=lambda x: x and ("bg-light-primary" in x or ("py-4" in x and "ms-n2" in x)),
        )

        jenis_bentuk_singkat = ""
        bentuk_full = ""

        for section in metadata_sections:
            for row in section.find_all("div", class_="row"):
                cols = row.find_all("div", class_=lambda x: x and "col-lg" in x)
                if len(cols) < 2:
                    continue

                label = cols[0].get_text(strip=True).lower()
                value = cols[1].get_text(strip=True)
                if not value:
                    continue

                if "bentuk singkat" in label:
                    jenis_bentuk_singkat = value
                elif "tipe dokumen" in label or "tipe" in label:
                    if not jenis_bentuk_singkat:
                        jenis_bentuk_singkat = value
                elif "judul" in label:
                    details["tentang"] = value
                elif "t.e.u" in label or "teu" in label:
                    details["instansi"] = value.split(",", 1)[1].strip() if "," in value else value
                elif "nomor" in label and "bentuk" not in label:
                    details["nomor"] = value
                elif "tahun" in label:
                    details["tahun"] = value
                elif "bentuk" in label and "singkat" not in label:
                    bentuk_full = value
                    if not jenis_bentuk_singkat:
                        jenis_bentuk_singkat = value
                elif "tanggal penetapan" in label or "ditetapkan" in label or "tanggal dikeluarkan" in label:
                    details["tanggal_ditetapkan"] = convert_date_format(value)
                elif "tanggal pengundangan" in label or "diundangkan" in label:
                    details["tanggal_diundangkan"] = convert_date_format(value)
                elif "tanggal berlaku" in label or "berlaku" in label:
                    details["tanggal_berlaku"] = convert_date_format(value)

        for link in soup.find_all("a", class_=lambda x: x and "preview-pdf" in x):
            link_text = link.get_text(strip=True)
            if "lampiran" in link_text.lower():
                filename = link_text[:-4] if link_text.lower().endswith(".pdf") else link_text
                if filename not in details["lampiran"]:
                    details["lampiran"].append(filename)

        for lst in soup.find_all(["ol", "ul"]):
            prev_texts = lst.find_all_previous(string=True, limit=10)
            jenis_relasi = None
            for prev_text in prev_texts:
                t = prev_text.strip().lower()
                if "mencabut" in t and "dicabut" not in t:
                    jenis_relasi = "mencabut"
                    break
                if "dicabut" in t and "mencabut" not in t:
                    jenis_relasi = "dicabut"
                    break
                if "mengubah" in t and "diubah" not in t:
                    jenis_relasi = "mengubah"
                    break
                if "diubah" in t and "mengubah" not in t:
                    jenis_relasi = "diubah"
                    break

            if not jenis_relasi or jenis_relasi in details["status"]:
                continue

            first_item = lst.find("li")
            if not first_item:
                continue
            alink = first_item.find("a", href=True)
            if not alink:
                continue

            title = alink.get_text(strip=True)
            m = re.search(r"Peraturan\s+([A-Z]+)\s+No\.\s*(\d+)\s+Tahun\s+(\d{4})", title, re.IGNORECASE)
            if m:
                identifier = f"Peraturan {m.group(1).upper()} {m.group(2)}/{m.group(3)}"
            else:
                m2 = re.search(r"([A-Z]+)\s+(?:No\.\s*)?(\d+)[/\s]+(?:Tahun\s+)?(\d{4})", title, re.IGNORECASE)
                identifier = f"{m2.group(1).upper()} {m2.group(2)}/{m2.group(3)}" if m2 else title

            details["status"][jenis_relasi] = identifier

        bentuk_lower = (bentuk_full or "").lower()
        if "menteri" in bentuk_lower:
            details["jenis"] = "KEPMEN" if "keputusan" in bentuk_lower else "PERMEN"
        else:
            details["jenis"] = jenis_bentuk_singkat or ""

        if details["jenis"] and details["nomor"] and details["tahun"]:
            details["nama_file"] = f"{details['jenis']} Nomor {details['nomor']} Tahun {details['tahun']}"

        materi = parse_materi_pokok_from_soup(soup)
        if materi:
            details["description"] = materi

        terkait = parse_abstrak_peraturan_from_soup(soup)
        if terkait:
            details["peraturan_terkait"] = terkait

        return details

    except Exception as e:
        logger.error("Error detail %s: %s", detail_url, e, exc_info=True)
        return None


def to_upsert_sql(d: Dict[str, Any]) -> str:
    """
    Build ONE UPSERT statement.
    NOTE: uses now() on DB side for updated_at.
    """
    return f"""
INSERT INTO data_jdih.produk_hukum (
  id_source, jenis, instansi, nomor, tahun, tentang, description,
  status, tanggal_ditetapkan, tanggal_diundangkan, tanggal_berlaku,
  nama_file, source_url, source_url_download, lampiran, peraturan_terkait, updated_at
) VALUES (
  {sql_quote(d.get("id_source"))},
  {sql_quote(d.get("jenis"))},
  {sql_quote(d.get("instansi"))},
  {sql_quote(d.get("nomor"))},
  {sql_quote(d.get("tahun"))},
  {sql_quote(d.get("tentang"))},
  {sql_quote(d.get("description"))},
  {sql_jsonb(d.get("status") or {})},
  {sql_quote(d.get("tanggal_ditetapkan") or None)},
  {sql_quote(d.get("tanggal_diundangkan") or None)},
  {sql_quote(d.get("tanggal_berlaku") or None)},
  {sql_quote(d.get("nama_file"))},
  {sql_quote(d.get("source_url"))},
  {sql_quote(d.get("source_url_download"))},
  {sql_text_array(d.get("lampiran") or [])},
  {sql_jsonb(d.get("peraturan_terkait") or {})},
  now()
)
ON CONFLICT (id_source) DO UPDATE SET
  jenis = EXCLUDED.jenis,
  instansi = EXCLUDED.instansi,
  nomor = EXCLUDED.nomor,
  tahun = EXCLUDED.tahun,
  tentang = EXCLUDED.tentang,
  description = EXCLUDED.description,
  status = EXCLUDED.status,
  tanggal_ditetapkan = EXCLUDED.tanggal_ditetapkan,
  tanggal_diundangkan = EXCLUDED.tanggal_diundangkan,
  tanggal_berlaku = EXCLUDED.tanggal_berlaku,
  nama_file = EXCLUDED.nama_file,
  source_url = EXCLUDED.source_url,
  source_url_download = EXCLUDED.source_url_download,
  lampiran = EXCLUDED.lampiran,
  peraturan_terkait = EXCLUDED.peraturan_terkait,
  updated_at = now()
;
""".strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="JDIH Scraper -> outputs SQL UPSERT statements for NiFi PutSQL.")
    ap.add_argument("--type-url", default="https://peraturan.bpk.go.id/Search?jenis=")
    ap.add_argument("--type-name", default="Search (jenis kosong)")
    ap.add_argument("--years", default="")
    ap.add_argument("--max-days-ago", type=int, default=30)
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--limit-links", type=int, default=0)
    ap.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    args = ap.parse_args()

    setup_logging(args.log_level)

    year_filter: Optional[List[int]] = None
    if args.years.strip():
        year_filter = [int(x.strip()) for x in args.years.split(",") if x.strip()]

    links = scrape_regulations_by_type(
        type_url=args.type_url,
        type_name=args.type_name,
        year_filter=year_filter,
        max_days_ago=args.max_days_ago,
        sleep_seconds=args.sleep,
    )

    if args.limit_links and args.limit_links > 0:
        links = links[: args.limit_links]

    logger.info("Links to process: %s", len(links))

    # Output: many SQL statements (PutSQL can execute content)
    out_sql_parts: List[str] = []
    ok = 0

    for i, link in enumerate(links, 1):
        logger.info("[%s/%s] %s", i, len(links), (link.get("title") or "")[:80])
        d = scrape_regulation_details(link["url"])
        if d:
            out_sql_parts.append(to_upsert_sql(d))
            ok += 1
        time.sleep(args.sleep)

    # Write SQL to stdout
    sys.stdout.write("\n".join(out_sql_parts) + ("\n" if out_sql_parts else ""))
    sys.stdout.flush()

    logger.info("Done. details_ok=%s", ok)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())