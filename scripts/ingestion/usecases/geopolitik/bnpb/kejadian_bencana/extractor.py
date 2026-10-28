"""BNPB disaster events (Data Informasi Bencana Indonesia).

The Hub page only offers a manual Excel download, so this extractor tries, in order:
1. ``source_file`` - local ``.xlsx`` saved from the Hub page.
2. ``download_url`` (or a ``url`` ending in ``.xlsx``) - Excel fetched over HTTP.
3. ``url`` - ArcGIS FeatureServer ``/query`` (default: ``Data_Bencana_Dashboard``),
   paginated. The BNPB hosted data store answers HTTP 500 at the time of writing,
   which surfaces as ``SourceUnavailable`` with a hint to use 1 or 2.

Both Excel headers (dictionary labels such as ``Kode Identitas Bencana``) and
ArcGIS field names (``kib``, ``nkab``, ``nprop``, ``tahun/bulan/tanggal``) are accepted.
"""

from __future__ import annotations

import datetime as dt
import io
import logging
import re
from typing import Any, Dict, Iterable, Iterator, List, Optional

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://gis.bnpb.go.id/server/rest/services/Hosted/Data_Bencana_Dashboard/FeatureServer/0/query"
)
PAGE_SIZE = 1000
HINT = "set DOWNLOAD_URL or SOURCE_FILE to an Excel exported from the BNPB Data Bencana Hub page"

ALIASES = {
    "no": "no",
    "kode_identitas_bencana": "kode_identitas_bencana",
    "kib": "kode_identitas_bencana",
    "id_kabupaten": "id_kabupaten",
    "level1": "id_kabupaten",
    "tanggal_kejadian": "tanggal_kejadian",
    "kejadian": "kejadian",
    "lokasi": "lokasi",
    "kabupaten": "kabupaten",
    "nkab": "kabupaten",
    "provinsi": "provinsi",
    "nprop": "provinsi",
    "kronologi_dokumentasi": "kronologi_dokumentasi",
    "link_dokumentasi": "kronologi_dokumentasi",
    "penyebab": "penyebab",
    "meninggal": "meninggal",
    "hilang": "hilang",
    "terluka": "terluka",
    "rumah_rusak": "rumah_rusak",
    "rumah_terendam": "rumah_terendam",
    "terendam": "rumah_terendam",
    "fasum_rusak": "fasum_rusak",
}
INT_FIELDS = (
    "no", "id_kabupaten", "meninggal", "hilang", "terluka",
    "rumah_rusak", "rumah_terendam", "fasum_rusak",
)


def normalize_key(key: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")


def to_int(value: Any) -> Optional[int]:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(float(str(value).replace(",", "").strip()))
    except ValueError:
        return None


def to_date(value: Any) -> Optional[dt.date]:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, (int, float)) and value > 10_000_000_000:  # ArcGIS epoch ms
        return dt.datetime.fromtimestamp(value / 1000, dt.timezone.utc).date()
    if isinstance(value, str):
        text = value.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                return dt.datetime.strptime(text[:19] if "H" in fmt else text[:10], fmt).date()
            except ValueError:
                continue
    return None


def clean_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).replace("\\n", "\n")
    text = ", ".join(part.strip() for part in text.splitlines() if part.strip())
    return text or None


def map_row(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Map one Excel/ArcGIS row to dictionary-named fields; None when it has no date."""
    norm = {normalize_key(k): v for k, v in raw.items()}
    out: Dict[str, Any] = {}
    for key, value in norm.items():
        target = ALIASES.get(key)
        if target and out.get(target) is None:
            out[target] = value

    tanggal = to_date(out.get("tanggal_kejadian"))
    if tanggal is None:
        year, month, day = to_int(norm.get("tahun")), to_int(norm.get("bulan")), to_int(norm.get("tanggal"))
        if year and month and day:
            try:
                tanggal = dt.date(year, month, day)
            except ValueError:
                tanggal = None
    if tanggal is None:
        return None
    out["tanggal_kejadian"] = tanggal.isoformat()

    for name in INT_FIELDS:
        out[name] = to_int(out.get(name))
    for name in ("kode_identitas_bencana", "kejadian", "kabupaten", "provinsi",
                 "kronologi_dokumentasi", "penyebab"):
        value = out.get(name)
        out[name] = str(value).strip() or None if value is not None else None
    out["lokasi"] = clean_text(out.get("lokasi"))
    for name in ("no", "id_kabupaten", "kode_identitas_bencana", "kejadian", "lokasi", "kabupaten",
                 "provinsi", "kronologi_dokumentasi", "penyebab", "meninggal", "hilang",
                 "terluka", "rumah_rusak", "rumah_terendam", "fasum_rusak"):
        out.setdefault(name, None)
    return out


def map_rows(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    mapped = [map_row(row) for row in rows]
    return [row for row in mapped if row is not None]


def parse_excel(source: Any) -> List[Dict[str, Any]]:
    """Read the first sheet of an xlsx (path or file-like) using the first header-like row."""
    from openpyxl import load_workbook

    workbook = load_workbook(source, read_only=True, data_only=True)
    sheet = workbook.active
    header: Optional[List[str]] = None
    rows: List[Dict[str, Any]] = []
    for values in sheet.iter_rows(values_only=True):
        if header is None:
            keys = [normalize_key(v) if v is not None else "" for v in values]
            if sum(1 for k in keys if k in ALIASES or k in ("tahun", "bulan")) >= 3:
                header = [str(v) if v is not None else "" for v in values]
            continue
        if all(v is None for v in values):
            continue
        rows.append(dict(zip(header, values)))
    workbook.close()
    if header is None:
        raise SourceUnavailable("BNPB Excel has no recognisable header row")
    return map_rows(rows)


def parse_arcgis_page(payload: Any, url: str = "") -> List[Dict[str, Any]]:
    if not isinstance(payload, dict):
        raise SourceUnavailable(f"Unexpected ArcGIS response from {url}")
    if payload.get("error"):
        raise SourceUnavailable(f"ArcGIS error {payload['error'].get('code')} at {url}; {HINT}")
    return [feat.get("attributes") or {} for feat in payload.get("features") or []]


class Extractor(BaseExtractor):
    def extract(self) -> Iterator[Dict[str, Any]]:
        source_file = self.config.get("source_file")
        download_url = self.config.get("download_url")
        url = self.config.get("url") or DEFAULT_URL

        if source_file:
            rows = parse_excel(str(source_file))
        elif download_url or url.lower().split("?")[0].endswith(".xlsx"):
            target = download_url or url
            logger.info("Downloading BNPB Excel: %s", target)
            resp = self.http.get(target, timeout=180)
            rows = parse_excel(io.BytesIO(resp.content))
        else:
            rows = self._query_arcgis(url)

        if not rows:
            raise SourceUnavailable(f"BNPB returned no dated disaster rows; {HINT}")
        yield from rows

    def _query_arcgis(self, url: str) -> List[Dict[str, Any]]:
        if "/query" not in url:
            raise ConfigError(f"BNPB url must be an ArcGIS .../query endpoint or an .xlsx: {url}")
        params: Dict[str, Any] = {
            "where": self.config.get("where") or "1=1",
            "outFields": "*",
            "returnGeometry": "false",
            "orderByFields": "objectid",
            "resultRecordCount": PAGE_SIZE,
            "f": "json",
        }
        collected: List[Dict[str, Any]] = []
        offset = 0
        while True:
            try:
                resp = self.http.get(url, params={**params, "resultOffset": offset}, timeout=90)
                payload = resp.json()
            except ValueError as exc:
                raise SourceUnavailable(f"BNPB ArcGIS returned non-JSON from {url}; {HINT}") from exc
            page = parse_arcgis_page(payload, url)
            collected.extend(map_rows(page))
            offset += len(page)
            if not page or not payload.get("exceededTransferLimit"):
                break
        return collected
