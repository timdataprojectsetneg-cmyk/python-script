"""Excel access — Kasus Perselisihan (satudata.kemnaker.go.id).

The workbook is source-specific:

- One sheet per month (``Januari`` … ``Desember``) plus a ``metadata`` sheet.
- A 3-row merged header, e.g.::

      Jenis Perselisihan | Jumlah Perselisihan | ... | Penyelesaian Perselisihan | Sisa Kasus
                         | Pusat Daerah Jumlah | Bipartit Mediasi(PB/Anjuran) ... Jumlah |

- A final ``Total`` row and a ``Sumber:`` note that must be skipped.

Because every source Excel differs, the parsing lives here and overrides the
generic :class:`ExcelExtractor._parse_excel`.
"""

from __future__ import annotations

import re
from io import BytesIO
from typing import Any, Dict, List, Optional

from .....core.extractors.excel_extractor import ExcelExtractor

# CSS class of the download button on the satudata landing page (varies per source).
DOWNLOAD_SELECTOR = "bg-satudata-800"
# satudata is a React SPA, so the download link is rendered client-side.
DYNAMIC = True

MONTHS = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6,
    "juli": 7, "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12,
}

# Canonical Jenis Perselisihan values used by the Pydantic model.
def _canonical_jenis(raw: Any) -> str:
    norm = _norm(raw)
    if norm.startswith("perselisihanhak"):
        return "Perselisihan Hak"
    if norm.startswith("perselisihankepentingan"):
        return "Perselisihan Kepentingan"
    if norm.startswith("perselisihanphk") or norm == "phk":
        return "PHK"
    if "serikat" in norm and ("pekerja" in norm or "buruh" in norm):
        return "Serikat Pekerja"
    return str(raw).strip()

# (output field, keywords that all must appear in the flattened header)
FIELD_KEYWORDS = (
    ("Jenis_Perselisihan", ("jenisperselisihan",)),
    ("Jumlah_Pusat", ("pusat",)),
    ("Jumlah_Daerah", ("daerah",)),
    ("Bipartit", ("bipartit",)),
    ("Mediasi_PB", ("mediasi", "pb")),
    ("Mediasi_Anjuran", ("mediasi", "anjuran")),
    ("Konsiliasi", ("konsiliasi",)),
    ("Arbitrasi", ("arbitrasi",)),
    ("Hakim_HI", ("hakim",)),
    ("Sisa_Kasus", ("sisakasus",)),
)


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
            records.extend(self._parse_sheet(name, frame.values.tolist()))
        return records

    def _header_row_index(self, matrix: List[List[Any]]) -> Optional[int]:
        for index, row in enumerate(matrix):
            if any("jenisperselisihan" in _norm(cell) for cell in row):
                return index
        return None

    def _column_map(self, headers: List[str]) -> Dict[str, int]:
        mapping: Dict[str, int] = {}
        for field, keywords in FIELD_KEYWORDS:
            for index, header in enumerate(headers):
                if all(keyword in header for keyword in keywords):
                    mapping[field] = index
                    break
        return mapping

    @staticmethod
    def _ffill(row: List[Any]) -> List[Any]:
        """Forward-fill blanks so merged header cells apply to their sub-columns."""
        out: List[Any] = []
        last: Any = None
        for cell in row:
            if not _is_blank(cell):
                last = cell
            out.append(last)
        return out

    def _year(self, matrix: List[List[Any]], header_index: int) -> Optional[str]:
        for row in matrix[:header_index]:
            for cell in row:
                match = re.search(r"(20\d{2})", str(cell or ""))
                if match:
                    return match.group(1)
        return None

    def _parse_sheet(self, sheet_name: str, matrix: List[List[Any]]) -> List[Dict[str, Any]]:
        header_index = self._header_row_index(matrix)
        if header_index is None:
            return []

        # Data starts at the first row whose first cell is a "Perselisihan ..." label.
        data_start = len(matrix)
        for index in range(header_index + 1, len(matrix)):
            first = _norm(matrix[index][0]) if matrix[index] else ""
            if first.startswith("perselisihan"):
                data_start = index
                break

        header_rows = matrix[header_index:data_start] or matrix[header_index : header_index + 1]
        header_rows = [self._ffill(row) for row in header_rows]
        width = max((len(row) for row in header_rows), default=0)
        headers: List[str] = []
        for col in range(width):
            parts = [_norm(row[col]) for row in header_rows if col < len(row) and not _is_blank(row[col])]
            headers.append("".join(parts))

        columns = self._column_map(headers)
        year = self._year(matrix, header_index)
        month = MONTHS.get(sheet_name.strip().lower())
        periode = f"{year}-{month:02d}" if year and month else sheet_name.strip()

        records: List[Dict[str, Any]] = []
        for row in matrix[data_start:]:
            if not row or _is_blank(row[0]):
                continue
            jenis_raw = _norm(row[0])
            if not jenis_raw.startswith("perselisihan"):
                continue  # skips "Total", "Sumber: ...", blank footer rows
            jenis = _canonical_jenis(row[0])

            record: Dict[str, Any] = {"Jenis_Perselisihan": jenis, "Periode": periode}
            for field, index in columns.items():
                if field == "Jenis_Perselisihan" or index >= len(row):
                    continue
                record[field] = _to_int(row[index])
            records.append(record)
        return records
