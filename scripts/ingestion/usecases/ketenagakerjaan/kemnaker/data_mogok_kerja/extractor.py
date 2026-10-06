"""Excel access — Data Mogok Kerja.

Same satudata source as the other Kemnaker datasets; only the workbook layout
differs. The ``mogok`` sheet has a two-row header (Excel rows 4-5):
No. | Provinsi | Kasus | Tenaga Kerja yang Terlibat (orang), preceded by a
title row and a 'Tahun <yyyy>' row.
"""

from __future__ import annotations

import re
from io import BytesIO
from typing import Any, Dict, List

import openpyxl

from .._satudata import SatuDataExcelExtractor
from .models import Record

SHEET = "mogok"
DATA_START = 5                # 0-based Excel row 6 (first data row)
TITLE_ROW = 1                 # 0-based Excel row 2 -> 'Tahun <yyyy>'
FIRST_DATA_COLUMN = 1         # 0-based; column 0 is 'No.'
# Fields derived from the sheet title/name, not read from a data column.
DERIVED_FIELDS = ("tahun",)


def _column_fields() -> List[str]:
    """Excel data columns follow the model's field order (minus derived fields)."""
    return [name for name in Record.model_fields if name not in DERIVED_FIELDS]


# Column index -> model field name, derived from the pydantic model.
FIELD_BY_COLUMN = {
    FIRST_DATA_COLUMN + offset: name for offset, name in enumerate(_column_fields())
}


class Extractor(SatuDataExcelExtractor):
    """Resolve the mogok-kerja workbook URL from the satudata API, then parse it."""

    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        merged.setdefault("sheet", SHEET)
        merged.setdefault("require_columns", "provinsi")
        merged.setdefault("skip_row_prefixes", "jumlah,sumber")
        super().__init__(merged)

    def _parse_excel(self, content: bytes) -> List[Dict[str, Any]]:
        workbook = openpyxl.load_workbook(BytesIO(content), data_only=True)
        worksheet = workbook[self.config.get("sheet", SHEET)]
        rows = list(worksheet.iter_rows(values_only=True))
        tahun = self._year(rows)

        records: List[Dict[str, Any]] = []
        for row in rows[DATA_START:]:
            record = {
                field: self._clean(row[column] if column < len(row) else None)
                for column, field in FIELD_BY_COLUMN.items()
            }
            if not self._is_data_row(record):
                continue
            record["tahun"] = tahun
            records.append(record)
        return records

    @staticmethod
    def _clean(value: Any) -> Any:
        if isinstance(value, str):
            return " ".join(value.split()) or None
        return value

    @staticmethod
    def _year(rows: List[tuple]) -> int | None:
        if len(rows) <= TITLE_ROW or not rows[TITLE_ROW]:
            return None
        match = re.search(r"(\d{4})", str(rows[TITLE_ROW][0]))
        return int(match.group(1)) if match else None
