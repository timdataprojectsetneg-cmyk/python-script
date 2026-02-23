import sys
import json
import time
import random
import logging
import argparse
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("jdih_bkpm_scraper")

BASE_API = "https://jdih.bkpm.go.id/api/document-search"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

SESSION = requests.Session()


# ---------------- Logging ----------------
def setup_logging(level: str = "INFO") -> None:
    lvl = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(lvl)
    h = logging.StreamHandler(stream=sys.stderr)
    h.setLevel(lvl)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
    logger.handlers = [h]


# ---------------- HTTP Helper ----------------
def http_get(url: str, params: dict, max_retries: int = 5) -> requests.Response:
    for attempt in range(max_retries):
        try:
            r = SESSION.get(url, headers=DEFAULT_HEADERS, params=params, timeout=30)
            if r.status_code < 400:
                return r

            if r.status_code == 429 or 500 <= r.status_code < 600:
                wait = min(2 ** attempt + random.uniform(0.5, 1.5), 60)
                logger.warning("Retry %s sleep %.1fs", attempt + 1, wait)
                time.sleep(wait)
                continue

            r.raise_for_status()

        except requests.RequestException as e:
            wait = min(2 ** attempt + random.uniform(0.5, 1.5), 60)
            logger.warning("Error retry %s sleep %.1fs (%s)", attempt + 1, wait, e)
            time.sleep(wait)

    raise RuntimeError("Failed after retries")


# ---------------- SQL Helpers ----------------
def sql_quote(s: Optional[str]) -> str:
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def sql_jsonb(obj: Any) -> str:
    j = json.dumps(obj or {}, ensure_ascii=False, separators=(",", ":"))
    return sql_quote(j) + "::jsonb"


def sql_text_array(arr: List[str]) -> str:
    if not arr:
        return "ARRAY[]::text[]"
    items = ["'" + x.replace("'", "''") + "'" for x in arr]
    return "ARRAY[" + ",".join(items) + "]::text[]"


# ---------------- Transform ----------------
def build_row(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id_source": str(doc.get("id")),
        "jenis": "KEPMEN",
        "instansi": "Kementerian Investasi / BKPM",
        "nomor": doc.get("regulation_number"),
        "tahun": doc.get("publication_year"),
        "tentang": doc.get("title"),
        "description": None,
        "status": {},
        "tanggal_ditetapkan": doc.get("establishment_date"),
        "tanggal_diundangkan": doc.get("establishment_date"),
        "tanggal_berlaku": None,
        "nama_file": doc.get("title_short"),
        "source_url": f"https://jdih.bkpm.go.id/id/search?document_type=Peraturan&regulation_type=Keputusan&regulation_year={doc.get("publication_year")}",
        "source_download_url": doc.get("document_file_url"),
        "lampiran": [],
        "peraturan_terkait": {},
    }


# ---------------- SQL Builder ----------------
def to_upsert_sql_many(rows: List[Dict[str, Any]], table_name: str) -> str:
    if not rows:
        return ""

    cols = (
        "id_source, jenis, instansi, nomor, tahun, tentang, description, "
        "status, tanggal_ditetapkan, tanggal_diundangkan, tanggal_berlaku, "
        "nama_file, source_url, source_download_url, lampiran, peraturan_terkait, updated_at"
    )

    values = []
    for d in rows:
        values.append(
            "("
            f"{sql_quote(d['id_source'])},"
            f"{sql_quote(d['jenis'])},"
            f"{sql_quote(d['instansi'])},"
            f"{sql_quote(d['nomor'])},"
            f"{sql_quote(d['tahun'])},"
            f"{sql_quote(d['tentang'])},"
            f"{sql_quote(d['description'])},"
            f"{sql_jsonb(d['status'])},"
            f"{sql_quote(d['tanggal_ditetapkan'])},"
            f"{sql_quote(d['tanggal_diundangkan'])},"
            f"{sql_quote(d['tanggal_berlaku'])},"
            f"{sql_quote(d['nama_file'])},"
            f"{sql_quote(d['source_url'])},"
            f"{sql_quote(d['source_download_url'])},"
            f"{sql_text_array(d['lampiran'])},"
            f"{sql_jsonb(d['peraturan_terkait'])},"
            "now()"
            ")"
        )

    sql = (
        f"INSERT INTO {table_name} ({cols}) VALUES "
        + ",".join(values)
        + " ON CONFLICT (id_source) DO UPDATE SET "
        "jenis=EXCLUDED.jenis,"
        "instansi=EXCLUDED.instansi,"
        "nomor=EXCLUDED.nomor,"
        "tahun=EXCLUDED.tahun,"
        "tentang=EXCLUDED.tentang,"
        "status=EXCLUDED.status,"
        "tanggal_ditetapkan=EXCLUDED.tanggal_ditetapkan,"
        "tanggal_diundangkan=EXCLUDED.tanggal_diundangkan,"
        "tanggal_berlaku=EXCLUDED.tanggal_berlaku,"
        "nama_file=EXCLUDED.nama_file,"
        "source_url=EXCLUDED.source_url,"
        "source_download_url=EXCLUDED.source_download_url,"
        "updated_at=now()"
    )

    return sql


# ---------------- MAIN ----------------
def main():
    parser = argparse.ArgumentParser(description="Scraper JDIH BKPM")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--table", default="data_jdih.all_produk_hukum")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logging(args.log_level)

    page = 1
    limit_per_page = 50
    collected = []

    while True:
        logger.info("Fetching page %s", page)

        params = {
            "page": page,
            "limit": limit_per_page,
            "document_type": "Peraturan",
            "regulation_type": "Keputusan",
            "regulation_year": args.year,
        }

        r = http_get(BASE_API, params)
        data = r.json()

        docs = data.get("allDocuments", [])
        if not docs:
            break

        collected.extend(docs)

        if args.limit and len(collected) >= args.limit:
            collected = collected[: args.limit]
            break

        total = data.get("documents_aggregate", {}).get("aggregate", {}).get("count", 0)
        if len(collected) >= total:
            break

        page += 1
        time.sleep(1.5 + random.uniform(0.2, 1.0))

    logger.info("Collected %s documents", len(collected))

    rows = [build_row(d) for d in collected]
    sql = to_upsert_sql_many(rows, args.table)

    if sql:
        print(sql)


if __name__ == "__main__":
    main()
