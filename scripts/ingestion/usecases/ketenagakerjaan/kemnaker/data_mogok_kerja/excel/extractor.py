"""Excel access — Data Mogok Kerja (satudata.kemnaker.go.id).

Workbook layout (source-specific):

- Sheet ``mogok`` (plus ``metadata``) with a title row, ``Tahun <year>``, then a
  2-row header::

      No. | Provinsi | Januari s.d Maret | ...
                      | Kasus | Tenaga Kerja yang Terlibat (orang)

- One row per province; blank counts mean zero.
- A final ``Jumlah`` total row and a ``Sumber :`` note that must be skipped.
"""

from __future__ import annotations

import re
from io import BytesIO
from typing import Any, Dict, List, Optional

from ......core.extractors.excel_extractor import ExcelExtractor

DOWNLOAD_SELECTOR = "bg-satudata-800"
DYNAMIC = True


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:  # NaN
        return True
    return isinstance(value, str) and not value.strip()


def _to_int(value: Any) -> Optional[int]:
    if _is_blank(value):
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


class Extractor(ExcelExtractor):
    """Renders the satudata page, discovers the .xlsx link, and parses it."""

    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        merged.setdefault("download_selector", DOWNLOAD_SELECTOR)
        if merged.get("dynamic") is None:
            merged["dynamic"] = DYNAMIC
        super().__init__(merged)

    def _parse_excel(self, content: bytes) -> List[Dict[str, Any]]:
        import pandas as pd

        sheets = pd.read_excel(BytesIO(content), sheet_name=None, header=None, engine="openpyxl")
        records: List[Dict[str, Any]] = []
        for name, frame in sheets.items():
            if name.strip().lower() == "metadata":
                continue
            records.extend(self._parse_sheet(frame.values.tolist()))
        return records

    def _parse_sheet(self, matrix: List[List[Any]]) -> List[Dict[str, Any]]:
        # Exact "Provinsi" header cell — the title row also contains the word.
        header_index = next(
            (i for i, row in enumerate(matrix) if any(_norm(c) == "provinsi" for c in row)), None
        )
        if header_index is None:
            return []

        data_start = len(matrix)
        for index in range(header_index + 1, len(matrix)):
            row = matrix[index]
            if len(row) > 1 and _to_int(row[0]) is not None and not _is_blank(row[1]):
                data_start = index
                break

        header_rows = [self._ffill(row) for row in (matrix[header_index:data_start] or [matrix[header_index]])]
        width = max((len(row) for row in header_rows), default=0)
        headers = [
            "".join(_norm(row[col]) for row in header_rows if col < len(row) and not _is_blank(row[col]))
            for col in range(width)
        ]

        def find_col(*keywords: str) -> Optional[int]:
            for index, header in enumerate(headers):
                if all(keyword in header for keyword in keywords):
                    return index
            return None

        provinsi_col = find_col("provinsi")
        kasus_col = find_col("kasus")
        tenaga_col = find_col("tenagakerja")
        if provinsi_col is None or kasus_col is None:
            return []

        year = self._year(matrix, header_index)
        period_label = matrix[header_index][kasus_col] if kasus_col < len(matrix[header_index]) else None
        if _is_blank(period_label):
            period_label = None
        periode = " ".join(part for part in (str(period_label) if period_label else None, year) if part) or None

        records: List[Dict[str, Any]] = []
        for row in matrix[data_start:]:
            if not row or len(row) <= provinsi_col or _is_blank(row[provinsi_col]):
                continue
            if _norm(row[0]) in ("jumlah", "total"):
                continue
            provinsi = str(row[provinsi_col]).strip()
            if not provinsi:
                continue
            records.append(
                {
                    "Periode": periode,
                    "Provinsi": provinsi,
                    "Jumlah_Kasus": (_to_int(row[kasus_col]) if kasus_col < len(row) else 0) or 0,
                    "Jumlah_Pekerja": (_to_int(row[tenaga_col]) if tenaga_col is not None and tenaga_col < len(row) else 0) or 0,
                }
            )
        return records

    @staticmethod
    def _ffill(row: List[Any]) -> List[Any]:
        out: List[Any] = []
        last: Any = None
        for cell in row:
            if not _is_blank(cell):
                last = cell
            out.append(last)
        return out

    @staticmethod
    def _year(matrix: List[List[Any]], header_index: int) -> Optional[str]:
        for row in matrix[:header_index]:
            for cell in row:
                match = re.search(r"(20\d{2})", str(cell or ""))
                if match:
                    return match.group(1)
        return None
