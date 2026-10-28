"""Caldara-Iacoviello Geopolitical Risk (GPR) monthly index.

Reads ``data_gpr_export.dta`` with ``pandas.read_stata`` (the ``.xls`` variant on
the same page needs the optional ``xlrd`` package). ``.xlsx`` URLs are read with
openpyxl.
"""

from __future__ import annotations

import io
import logging
import math
from typing import Any, Dict, Iterator, List

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.dta"
FIELDS = {"GPR": "gpr", "GPRT": "gprt", "GPRA": "gpra"}


def _float(value: Any) -> Any:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(number) else number


def frame_to_records(frame) -> List[Dict[str, Any]]:
    """Convert a GPR dataframe (month, GPR, GPRT, GPRA, ...) into records."""
    import pandas as pd

    missing = [c for c in ("month", *FIELDS) if c not in frame.columns]
    if missing:
        raise SourceUnavailable(f"GPR file lacks expected columns: {missing}")
    rows: List[Dict[str, Any]] = []
    for _, row in frame.iterrows():
        month = pd.to_datetime(row["month"], errors="coerce")
        if pd.isna(month):
            continue
        record: Dict[str, Any] = {"month": month.strftime("%Y-%m")}
        for src, name in FIELDS.items():
            record[name] = _float(row[src])
        if all(record[name] is None for name in FIELDS.values()):
            continue
        rows.append(record)
    return rows


def read_frame(content: bytes, url: str):
    import pandas as pd

    lowered = url.lower().split("?")[0]
    if lowered.endswith((".xlsx", ".xls")):
        try:
            return pd.read_excel(io.BytesIO(content))
        except ImportError as exc:
            raise ConfigError(f"Reading {lowered.rsplit('.', 1)[-1]} needs an extra package: {exc}") from exc
    return pd.read_stata(io.BytesIO(content))


class Extractor(BaseExtractor):
    def extract(self) -> Iterator[Dict[str, Any]]:
        url = self.config.get("url") or DEFAULT_URL
        logger.info("Downloading GPR file: %s", url)
        resp = self.http.get(url, timeout=180)
        rows = frame_to_records(read_frame(resp.content, url))
        if not rows:
            raise SourceUnavailable(f"GPR file at {url} contained no rows")
        yield from rows
