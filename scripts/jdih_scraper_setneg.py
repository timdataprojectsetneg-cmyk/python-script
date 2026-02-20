import sys
import os
import re
import json
import time
import random
import logging
import argparse
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger("jdih_setneg_scraper")

BASE = "https://jdih.setneg.go.id"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": BASE,
    "Referer": f"{BASE}/Produk",
    "Connection": "keep-alive",
}

SESSION = requests.Session()


def setup_logging(level: str = "INFO") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(lvl)
    h = logging.StreamHandler(stream=sys.stderr)
    h.setLevel(lvl)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
    logger.handlers = [h]


# ---------------- HTTP helper (429 backoff) ----------------
def http_get(
    url: str,
    headers: dict,
    timeout: int = 20,
    max_retries: int = 6,
    base_sleep: float = 2.5,
) -> requests.Response:
    last_exc: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            r = SESSION.get(url, headers=headers, timeout=timeout)
            if r.status_code < 400:
                return r

            if r.status_code == 429:
                retry_after = r.headers.get("Retry-After")
                if retry_after and str(retry_after).strip().isdigit():
                    wait = int(retry_after)
                else:
                    wait = base_sleep * (2**attempt) + random.uniform(0.5, 2.5)
                wait = min(wait, 120)
                logger.warning(
                    "429 Too Many Requests. Sleep %.1fs then retry (%s/%s): %s",
                    wait,
                    attempt + 1,
                    max_retries,
                    url,
                )
                time.sleep(wait)
                continue

            if 500 <= r.status_code < 600:
                wait = min(base_sleep * (2**attempt) + random.uniform(0.5, 2.5), 60)
                logger.warning(
                    "%s server error. Sleep %.1fs then retry (%s/%s): %s",
                    r.status_code,
                    wait,
                    attempt + 1,
                    max_retries,
                    url,
                )
                time.sleep(wait)
                continue

            r.raise_for_status()
            return r

        except requests.RequestException as e:
            last_exc = e
            wait = min(base_sleep * (2**attempt) + random.uniform(0.5, 2.5), 60)
            logger.warning(
                "RequestException. Sleep %.1fs then retry (%s/%s): %s (%s)",
                wait,
                attempt + 1,
                max_retries,
                url,
                e,
            )
            time.sleep(wait)

    if last_exc:
        raise last_exc
    raise RuntimeError(f"Failed to GET after retries: {url}")


def http_post(
    url: str,
    headers: dict,
    data: Any,
    timeout: int = 20,
    max_retries: int = 6,
    base_sleep: float = 2.5,
) -> requests.Response:
    last_exc: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            r = SESSION.post(url, headers=headers, data=data, timeout=timeout)
            if r.status_code < 400:
                return r

            if r.status_code == 429:
                retry_after = r.headers.get("Retry-After")
                if retry_after and str(retry_after).strip().isdigit():
                    wait = int(retry_after)
                else:
                    wait = base_sleep * (2**attempt) + random.uniform(0.5, 2.5)
                wait = min(wait, 120)
                logger.warning(
                    "429 Too Many Requests. Sleep %.1fs then retry (%s/%s): %s",
                    wait,
                    attempt + 1,
                    max_retries,
                    url,
                )
                time.sleep(wait)
                continue

            if 500 <= r.status_code < 600:
                wait = min(base_sleep * (2**attempt) + random.uniform(0.5, 2.5), 60)
                logger.warning(
                    "%s server error. Sleep %.1fs then retry (%s/%s): %s",
                    r.status_code,
                    wait,
                    attempt + 1,
                    max_retries,
                    url,
                )
                time.sleep(wait)
                continue

            r.raise_for_status()
            return r

        except requests.RequestException as e:
            last_exc = e
            wait = min(base_sleep * (2**attempt) + random.uniform(0.5, 2.5), 60)
            logger.warning(
                "RequestException. Sleep %.1fs then retry (%s/%s): %s (%s)",
                wait,
                attempt + 1,
                max_retries,
                url,
                e,
            )
            time.sleep(wait)

    if last_exc:
        raise last_exc
    raise RuntimeError(f"Failed to POST after retries: {url}")


# ---------------- SQL helpers ----------------
def sql_quote(s: Optional[str]) -> str:
    if s is None:
        return "NULL"
    s = str(s)
    return "'" + s.replace("'", "''") + "'"


def sql_jsonb(obj: Any) -> str:
    if obj is None:
        obj = {}
    # kalau string JSON sudah valid, keep; kalau dict/list, dump
    if isinstance(obj, str):
        try:
            parsed = json.loads(obj)
            obj = parsed
        except Exception:
            obj = {"raw": obj}
    j = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return sql_quote(j) + "::jsonb"


def sql_text_array(arr: Any) -> str:
    """
    Postgres text[] literal, with safe single-quote escaping.
    Important: element must be single-quoted, not ARRAY["..."] (itu dianggap identifier).
    """
    if not arr:
        return "ARRAY[]::text[]"
    if not isinstance(arr, list):
        arr = [arr]
    items = []
    for x in arr:
        if x is None:
            continue
        v = str(x).replace("'", "''")
        items.append(f"'{v}'")
    if not items:
        return "ARRAY[]::text[]"
    return "ARRAY[" + ",".join(items) + "]::text[]"


# ---------------- parsing helpers ----------------
def extract_peraturan_id(judul_html: str) -> Optional[str]:
    if isinstance(judul_html, str):
        m = re.search(r"view_function\('([^']+)'\)", judul_html)
        if m:
            return m.group(1)
    return None


def clean_html(text: str) -> str:
    if not isinstance(text, str):
        return text
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"[\n\r\t]+", " ", clean)
    clean = re.sub(r"\s+", " ", clean)
    return clean.strip()


def clean_date(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    if date_str == "0000-00-00":
        return None
    return date_str


def extract_terk_x_ids(terk_x: Any) -> Optional[Dict[str, List[str]]]:
    """
    terk_x bisa dict berisi jenis -> list/dict item. Ambil field 'id' (mis: "UU 24/2000").
    Output dict untuk disimpan sebagai jsonb.
    """
    if not terk_x or not isinstance(terk_x, dict):
        return None

    result: Dict[str, List[str]] = {}
    for jenis, items in terk_x.items():
        ids: List[str] = []

        if isinstance(items, dict):
            for _, item in items.items():
                if isinstance(item, dict):
                    item_id = item.get("id")
                    if item_id:
                        ids.append(item_id)

        elif isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    item_id = item.get("id")
                    if item_id:
                        ids.append(item_id)

        if ids:
            # dedup preserve order, then sort (biar stabil)
            ids = list(dict.fromkeys(ids))
            result[jenis] = sorted(ids)

    return result or None


# ---------------- rules requested ----------------
def jenis_titlecase_first_only(j: Optional[str]) -> Optional[str]:
    if not j:
        return None

    j = str(j).strip()
    if not j:
        return None

    j_upper = j.upper()

    if j_upper in ("UU", "PP"):
        return j_upper

    return j_upper[:1] + j_upper[1:].lower()

def map_jenis_instansi_from_list_value(jenis_list_val: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not jenis_list_val:
        return None, None

    j = str(jenis_list_val).strip().upper()
    if j == "PERMENSETNEG":
        return "PERMEN", "Kementerian Sekretariat Negara"
    if j == "KEPMENSESNEG":
        return "KEPMEN", "Kementerian Sekretariat Negara"
    return jenis_list_val, "Pemerintah Pusat"


# ---------------- API calls ----------------
def get_csrf_and_token(headers: dict, sleep: float) -> Tuple[str, str]:
    r_csrf = http_get(f"{BASE}/csrf", headers=headers, timeout=20)
    csrf = r_csrf.text.strip().strip('"')

    time.sleep(max(0.2, sleep) + random.uniform(0, 0.8))

    r_token = http_get(f"{BASE}/token", headers=headers, timeout=20)
    token = r_token.text.strip().strip('"')

    return csrf, token


def fetch_page(
    csrf: str,
    token: str,
    start: int,
    length: int,
    years: Optional[List[int]],
    headers: dict,
) -> Dict[str, Any]:
    payload = {
        "draw": "1",
        "columns[0][data]": "0",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "false",
        "columns[1][data]": "1",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[2][data]": "2",
        "columns[2][searchable]": "true",
        "columns[2][orderable]": "true",
        "columns[3][data]": "3",
        "columns[3][searchable]": "true",
        "columns[3][orderable]": "true",
        "columns[4][data]": "4",
        "columns[4][searchable]": "true",
        "columns[4][orderable]": "false",
        "columns[5][data]": "5",
        "columns[5][searchable]": "true",
        "columns[5][orderable]": "false",
        "start": str(start),
        "length": str(length),
        "search[value]": "",
        "search[regex]": "false",
        "CSRFToken": csrf,
        "Authorization": token,
    }

    payload_list = [(k, v) for k, v in payload.items()]

    if years:
        for y in years:
            payload_list.append(("tahun[]", str(y)))

    r = http_post(f"{BASE}/ProdukHukum", headers=headers, data=payload_list, timeout=25)
    return r.json()


def fetch_detail(peraturan_id: str, headers: dict) -> Optional[Dict[str, Any]]:
    """
    GET detail json: { data: {...}, terk_x: {...}, ... }
    """
    url = f"{BASE}/front/Peraturan/ajaxview?id={peraturan_id}"
    r = http_get(url, headers=headers, timeout=25)
    try:
        return r.json()
    except Exception:
        return None


# ---------------- transform to DB row ----------------
def build_row_from_item_and_detail(
    item: List[Any],
    peraturan_id: str,
    detail_payload: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    item indexes (dari /ProdukHukum):
      0 No, 1 Jenis, 2 Nomor, 3 Tahun, 4 Judul(html), 5 ID(?)
    """

    # dari list
    judul_html = item[4] if len(item) > 4 else ""
    tentang = clean_html(judul_html) if judul_html else None
    jenis_list_val = item[1] if len(item) > 1 else None
    nomor = item[2] if len(item) > 2 else None
    tahun = item[3] if len(item) > 3 else None

    # mapping jenis+instansi
    mapped_jenis, mapped_instansi = map_jenis_instansi_from_list_value(jenis_list_val)
    jenis = mapped_jenis
    instansi = mapped_instansi or "Pemerintah Pusat"

    # nama_file: "Perpres Nomor 63 Tahun 2017" (jenis title-case first letter only)
    jenis_fmt = jenis_titlecase_first_only(jenis) or ""
    nomor_str = str(nomor).strip() if nomor is not None else ""
    tahun_str = str(tahun).strip() if tahun is not None else ""
    nama_file_fmt = None
    if jenis_fmt and nomor_str and tahun_str:
        nama_file_fmt = f"{jenis_fmt} Nomor {nomor_str} Tahun {tahun_str}"

    # defaults
    status_obj: Dict[str, Any] = {}
    tanggal_ditetapkan = None
    tanggal_diundangkan = None
    tanggal_berlaku = None
    source_download_url = None
    peraturan_terkait = None

    # id_source: prefer detail.data.idperaturan
    id_source = peraturan_id

    # detail
    if detail_payload and isinstance(detail_payload, dict):
        d = detail_payload.get("data") or {}
        terk_x = detail_payload.get("terk_x")

        for k in ("mengubah", "mencabut", "diubah", "dicabut"):
            v = d.get(k)
            if v:
                status_obj[k] = v

        tanggal_ditetapkan = clean_date(d.get("tgl_di"))
        tanggal_diundangkan = clean_date(d.get("tgl_diun")) or clean_date(d.get("diundangkan"))
        tanggal_berlaku = clean_date(d.get("tgl_sah"))

        # ambil download dari url2 (sesuai request)
        datafile = d.get("datafile")
        if isinstance(datafile, list) and datafile:
            f0 = datafile[0] if isinstance(datafile[0], dict) else {}
            source_download_url = f0.get("url2") or f0.get("url1") or f0.get("url") or None

        peraturan_terkait = extract_terk_x_ids(terk_x)

        id_source = d.get("idperaturan") or peraturan_id

    row = {
        "id_source": str(id_source) if id_source is not None else None,
        "jenis": str(jenis) if jenis is not None else None,
        "instansi": instansi,
        "nomor": str(nomor) if nomor is not None else None,
        "tahun": str(tahun) if tahun is not None else None,
        "tentang": tentang,
        "description": None,
        "status": status_obj or {},
        "tanggal_ditetapkan": tanggal_ditetapkan,
        "tanggal_diundangkan": tanggal_diundangkan,
        "tanggal_berlaku": tanggal_berlaku,
        "nama_file": nama_file_fmt,  # sesuai request (bukan basename)
        "source_url": "https://jdih.setneg.go.id",  # sesuai request: seragam
        "source_download_url": source_download_url,  # sesuai request: dari url2
        "lampiran": [],
        "peraturan_terkait": peraturan_terkait or {},
    }

    if not row["id_source"]:
        return None
    return row


def to_upsert_sql_many(rows: List[Dict[str, Any]], table_name: str) -> str:
    """
    ONE INSERT statement with MANY VALUES + ON CONFLICT.
    No trailing semicolon (lebih aman untuk JDBC/PutSQL).
    """
    if not rows:
        return ""

    cols = (
        "id_source, jenis, instansi, nomor, tahun, tentang, description, "
        "status, tanggal_ditetapkan, tanggal_diundangkan, tanggal_berlaku, "
        "nama_file, source_url, source_download_url, lampiran, peraturan_terkait, updated_at"
    )

    values_parts: List[str] = []
    for d in rows:
        values_parts.append(
            "("
            f"{sql_quote(d.get('id_source'))},"
            f"{sql_quote(d.get('jenis'))},"
            f"{sql_quote(d.get('instansi'))},"
            f"{sql_quote(d.get('nomor'))},"
            f"{sql_quote(d.get('tahun'))},"
            f"{sql_quote(d.get('tentang'))},"
            f"{sql_quote(d.get('description'))},"
            f"{sql_jsonb(d.get('status') or {})},"
            f"{sql_quote(d.get('tanggal_ditetapkan') or None)},"
            f"{sql_quote(d.get('tanggal_diundangkan') or None)},"
            f"{sql_quote(d.get('tanggal_berlaku') or None)},"
            f"{sql_quote(d.get('nama_file'))},"
            f"{sql_quote(d.get('source_url'))},"
            f"{sql_quote(d.get('source_download_url'))},"
            f"{sql_text_array(d.get('lampiran') or [])},"
            f"{sql_jsonb(d.get('peraturan_terkait') or {})},"
            "now()"
            ")"
        )

    values_sql = ",".join(values_parts)

    sql = (
        f"INSERT INTO {table_name} ({cols}) VALUES {values_sql} "
        "ON CONFLICT (id_source) DO UPDATE SET "
        "jenis=EXCLUDED.jenis,"
        "instansi=EXCLUDED.instansi,"
        "nomor=EXCLUDED.nomor,"
        "tahun=EXCLUDED.tahun,"
        "tentang=EXCLUDED.tentang,"
        "description=EXCLUDED.description,"
        "status=EXCLUDED.status,"
        "tanggal_ditetapkan=EXCLUDED.tanggal_ditetapkan,"
        "tanggal_diundangkan=EXCLUDED.tanggal_diundangkan,"
        "tanggal_berlaku=EXCLUDED.tanggal_berlaku,"
        "nama_file=EXCLUDED.nama_file,"
        "source_url=EXCLUDED.source_url,"
        "source_download_url=EXCLUDED.source_download_url,"
        "lampiran=EXCLUDED.lampiran,"
        "peraturan_terkait=EXCLUDED.peraturan_terkait,"
        "updated_at=now()"
    )
    return sql


def main() -> int:
    ap = argparse.ArgumentParser(
        description="JDIH Setneg scraper -> outputs ONE SQL UPSERT statement for NiFi PutSQL."
    )
    ap.add_argument(
        "--years",
        default="",
        help="Comma-separated years, e.g. 2024,2025. Empty = all years.",
    )
    ap.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Paging size for ProdukHukum endpoint.",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit total records (0 = no limit).",
    )
    ap.add_argument(
        "--fetch-details",
        type=int,
        default=1,
        help="1 = fetch detail per id, 0 = only list page.",
    )
    ap.add_argument(
        "--sleep",
        type=float,
        default=2.0,
        help="Base sleep between requests.",
    )
    ap.add_argument(
        "--table",
        default="data_jdih.all_produk_hukum",
        help="Target table name.",
    )
    ap.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    args = ap.parse_args()

    setup_logging(args.log_level)

    years: Optional[List[int]] = None
    if args.years.strip():
        years = [int(x.strip()) for x in args.years.split(",") if x.strip()]

    logger.info("Getting CSRF + token...")
    csrf, token = get_csrf_and_token(DEFAULT_HEADERS, sleep=args.sleep)
    logger.info("CSRF/token OK")

    start = 0
    total_records = None
    collected_items: List[List[Any]] = []

    while True:
        logger.info("Fetching page: start=%s length=%s", start, args.batch_size)
        data = fetch_page(
            csrf=csrf,
            token=token,
            start=start,
            length=args.batch_size,
            years=years,
            headers=DEFAULT_HEADERS,
        )

        items = data.get("data", []) or []
        if total_records is None:
            total_records = data.get("recordsFiltered", 0) or 0
            logger.info("Total recordsFiltered=%s", total_records)

        if not items:
            break

        collected_items.extend(items)

        if args.limit and args.limit > 0 and len(collected_items) >= args.limit:
            collected_items = collected_items[: args.limit]
            logger.info("Reached limit=%s", args.limit)
            break

        if total_records and len(collected_items) >= total_records:
            break

        start += args.batch_size
        time.sleep(max(0.2, args.sleep) + random.uniform(0, 1.0))

    logger.info("Items collected=%s", len(collected_items))

    rows: List[Dict[str, Any]] = []
    fetch_details_flag = bool(args.fetch_details)

    for idx, item in enumerate(collected_items, 1):
        try:
            judul_html = item[4] if len(item) > 4 else ""
            peraturan_id = extract_peraturan_id(judul_html)
            if not peraturan_id:
                continue

            detail_payload = None
            if fetch_details_flag:
                logger.info("[%s/%s] detail %s", idx, len(collected_items), peraturan_id)
                detail_payload = fetch_detail(peraturan_id, DEFAULT_HEADERS)

            row = build_row_from_item_and_detail(
                item=item,
                peraturan_id=peraturan_id,
                detail_payload=detail_payload,
            )
            if row:
                rows.append(row)

            time.sleep(max(0.2, args.sleep) + random.uniform(0, 1.2))

        except Exception as e:
            logger.warning("Skip item idx=%s due to error: %s", idx, e, exc_info=True)
            continue

    logger.info("Rows ready=%s", len(rows))

    sql = to_upsert_sql_many(rows, table_name=args.table)
    if sql:
        sys.stdout.write(sql + "\n")
        sys.stdout.flush()
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())