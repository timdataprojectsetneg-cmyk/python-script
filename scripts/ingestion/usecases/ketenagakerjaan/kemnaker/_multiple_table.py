"""Shared extractor base for satudata workbooks that stack several tables per sheet.

One sheet may hold more than one table, each opened by a text marker (in the
Kemnaker workbooks e.g. ``Tabel 1`` = per skala perusahaan, ``Tabel 2`` = per
lapangan usaha). A subclass sets ``table_marker`` — the table it needs — and may
override ``table_markers`` with every marker present in the workbook: the markers
bound each other, so parsing with a single marker would let the next table's rows
bleed into the requested one. Records from every data sheet are unioned.

The generic engine names wide-table columns after the full header path
(``s.d. Januari > Mikro`` -> ``s_d_januari_mikro``), so columns are renamed to
the header leaf (``mikro``) to match the source's Pydantic model. Period/group
information is not part of the column name: it stays in ``_sheet_name`` (which a
normalizer can map to its own column, e.g. ``bulan``).
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

from ....core.extractors.excel_automation import extract_workbook, slugify, to_records
from ._satudata import SatuDataExcelExtractor

# Marker yang umum di workbook satudata Kemnaker; ganti lewat ``table_markers``
# bila workbook sumber memakai penanda lain.
TABLE_MARKERS = ["Tabel 1", "Tabel 2"]


def _leaf_names(colmeta: List[Dict[str, Any]], table: str) -> Dict[str, str]:
    """Map wide-table columns to their header leaf (``s.d. Januari > Mikro`` -> ``mikro``)."""
    names: Dict[str, str] = {}
    for column in colmeta:
        if column.get("table_name") != table:
            continue
        path = column.get("header_path") or ""
        if path:
            names[column["column_name"]] = slugify(path.split(">")[-1])
    return names


class MultipleTableExtractor(SatuDataExcelExtractor):
    """Take one marker-delimited table out of every sheet and union them."""

    table_marker = "Tabel 1"
    table_markers: Optional[List[str]] = None

    def extract(self) -> Iterator[Dict[str, Any]]:
        content = self._download(self._resolve_download_url()).content
        result = extract_workbook(
            content,
            outputs=["data"],
            profile=False,
            relations=False,
            table_markers=self.table_markers or TABLE_MARKERS,
        )
        wanted = f"_{slugify(self.table_marker)}_data"
        for sheet in result.sheets:
            if not sheet.table_wide.endswith(wanted):
                continue
            wide = sheet.wide.rename(columns=_leaf_names(sheet.colmeta, sheet.table_wide))
            yield from to_records(wide)
