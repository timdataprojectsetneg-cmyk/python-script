"""Shared extractor base for satudata.kemnaker.go.id Excel datasets.

The ``/data/kumpulan-data/<id>`` detail page is a client-rendered SPA: the
``bg-satudata-800`` download button only exists after JavaScript runs. That
button's ``href`` is hydrated from the public ``list_data`` API, so this base
resolves the ``.xlsx`` URL from the same API (using the dataset id in the
landing URL) before parsing the workbook.

Subclass this and set the source's ``sheet``/``header_row`` (and override
``_parse_excel`` when the layout is not a single header row), e.g.::

    class Extractor(SatuDataExcelExtractor):
        ...
"""

from __future__ import annotations

import re
from typing import Any, Dict

from ....core.extractors.excel_extractor import ExcelExtractor
from ....exceptions import SourceUnavailable

# Download button class on the satudata page (the SPA hydrates its href from the API).
DOWNLOAD_SELECTOR = "bg-satudata-800"
# Public endpoint the SPA uses to build the download link; supports page/limit.
LIST_DATA_API = "https://satudata.kemnaker.go.id/api/v1/data/list_data"
DATASET_ID_RE = re.compile(r"/kumpulan-data/(\d+)")
PAGE_SIZE = 1000


class SatuDataExcelExtractor(ExcelExtractor):
    """ExcelExtractor that resolves its download URL from the satudata API."""

    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
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
        """Page the public ``list_data`` API until ``dataset_id`` is found."""
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
