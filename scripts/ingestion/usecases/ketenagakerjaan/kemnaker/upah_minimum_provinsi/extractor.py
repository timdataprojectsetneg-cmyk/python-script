"""Excel access — Upah Minimum Provinsi (UMP).

The detail page (``/data/kumpulan-data/3005``) is a client-rendered SPA: the
``bg-satudata-800`` download button only exists after JavaScript runs. That
button's ``href`` is hydrated from the public ``list_data`` API, so this
extractor resolves the .xlsx URL from the same API (using the dataset id in the
landing URL) before parsing the workbook.
"""

from __future__ import annotations

import re
from typing import Any, Dict

from .....core.extractors.excel_extractor import ExcelExtractor
from .....exceptions import SourceUnavailable

# 0-based header row (Excel row 4): No | Provinsi | Upah Minimum (Rp).
SHEET = "data"
HEADER_ROW = 3
# Drop non-province rows (aggregate 'Rata-Rata' and 'Sumber: ...' footer).
REQUIRE_COLUMNS = "Provinsi"
SKIP_ROW_PREFIXES = "sumber,rata-rata"
# Download button class on the satudata page (the SPA hydrates its href from the API).
DOWNLOAD_SELECTOR = "bg-satudata-800"
# Public endpoint the SPA uses to build the download link; supports page/limit.
LIST_DATA_API = "https://satudata.kemnaker.go.id/api/v1/data/list_data"
DATASET_ID_RE = re.compile(r"/kumpulan-data/(\d+)")
PAGE_SIZE = 1000


class Extractor(ExcelExtractor):
    """Resolve the UMP workbook URL from the satudata API, then parse its rows."""

    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        merged.setdefault("sheet", SHEET)
        merged.setdefault("header_row", HEADER_ROW)
        merged.setdefault("require_columns", REQUIRE_COLUMNS)
        merged.setdefault("skip_row_prefixes", SKIP_ROW_PREFIXES)
        merged.setdefault("download_selector", DOWNLOAD_SELECTOR)
        super().__init__(merged)


    def _resolve_download_url(self) -> str:
        from_step = self.config.get("download_url")
        if from_step:
            return str(from_step)
        url = self.url or ""
        if url.lower().endswith((".xlsx", ".xls", ".xlsm")):
            return url
        match = DATASET_ID_RE.search(url)
        if not match:
            return super()._resolve_download_url()
        return self._resolve_from_api(int(match.group(1)))

    def _resolve_from_api(self, dataset_id: int) -> str:
        page = 1
        while page <= 20:
            resp = self.http.request(
                "GET",
                LIST_DATA_API,
                params={"ketenagakerjaan": "", "search": "", "page": page, "limit": PAGE_SIZE},
                timeout=60,
            )
            try:
                payload = resp.json()
            except ValueError as exc:
                raise SourceUnavailable(f"Invalid JSON response from {LIST_DATA_API}") from exc
            data = payload.get("data") if isinstance(payload, dict) else None
            rows = data.get("data") if isinstance(data, dict) else None
            if not isinstance(rows, list) or not rows:
                break
            found = next(
                (row for row in rows if row.get("id") == dataset_id and row.get("file")), None
            )
            if found:
                return found["file"]
            total = data.get("total")
            if isinstance(total, int) and page * PAGE_SIZE >= total:
                break
            page += 1
        raise SourceUnavailable(
            f"Excel file for dataset id={dataset_id} not found via {LIST_DATA_API}"
        )
