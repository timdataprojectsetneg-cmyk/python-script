"""Kemlu Riwayat Evakuasi WNI: evacuation summary table of the Renstra Dit. PWNI 2025-2029 PDF.

The table (Tahun | Negara | Jenis Kondisi | Jumlah Evacuees) starts at a header
at the bottom of one page and its rows sit on the next page(s), read until the
first non-table text after the rows (no page cap), so the text is read
in pypdf layout mode and split into columns by x offset. Wrapped cells are
re-joined per column. This is a historical summary in a strategic plan, not an
active contingency plan. ``URL`` (default constant) or ``SOURCE_FILE`` selects the PDF.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .....core.base.extractor import BaseExtractor
from .....exceptions import SourceUnavailable
from .._pdf import load_pdf, read_pages

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://kemlu.go.id/files/repositori/65391/177303099769ae4e55132b7_Renstra_Direktorat_PWNI_2025_2029.pdf"
)

HEADER = re.compile(r"Tahun\s+Negara\s+Jenis\s+Kondisi\s+Jumlah\s+Evacuees", re.I)
_ROW = re.compile(r"^\s*(20\d{2}|19\d{2})\s{2,}\S")
_CELL = re.compile(r"\S+(?: \S+)*")
_FOOTER = re.compile(r"^\s*\d+\s*\|")
_COUNTRY_ALIASES = {"RRT": "China"}  # Republik Rakyat Tiongkok
_COUNTRY_SPLIT = re.compile(r",\s*(?:dan\s+)?|\s+dan\s+", re.I)


def cells_of(line: str) -> List[Tuple[int, str]]:
    return [(m.start(), m.group()) for m in _CELL.finditer(line)]


def parse_count(text: str, unit: str) -> Optional[int]:
    m = re.search(rf"(\d{{1,3}}(?:\.\d{{3}})+|\d+)\s*{unit}\b", text, re.I)
    return int(m.group(1).replace(".", "")) if m else None


def normalize_country(text: str) -> str:
    parts = [p.strip() for p in _COUNTRY_SPLIT.split(" ".join(text.split())) if p.strip()]
    return "; ".join(_COUNTRY_ALIASES.get(p, p) for p in parts)


def parse_evacuations(pages: List[str]) -> List[Dict[str, Any]]:
    """Evacuation rows from layout-mode page texts (page numbers are 1-based)."""
    start = next((i for i, t in enumerate(pages) if HEADER.search(t)), None)
    if start is None:
        return []
    rows: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    columns: List[int] = []
    done = False

    def flush() -> None:
        nonlocal current
        if current is None:
            return
        cell = {k: " ".join(v).strip() for k, v in current["cells"].items()}
        jumlah = cell.get("jumlah", "")
        rows.append(
            {
                "tahun": int(cell["tahun"]),
                "negara_wilayah": normalize_country(cell.get("negara", "")) or None,
                "konteks": " ".join(cell.get("konteks", "").split()) or None,
                "wni_dievakuasi": parse_count(jumlah, "WNI"),
                "wna_dievakuasi": parse_count(jumlah, "WNA"),
                "halaman_pdf": current["page"],
            }
        )
        current = None

    for offset, text in enumerate(pages[start:]):
        page_no = start + offset + 1
        lines = text.splitlines()
        if offset == 0:
            header_at = next(i for i, ln in enumerate(lines) if HEADER.search(ln))
            lines = lines[header_at + 1 :]
        for line in lines:
            if not line.strip():
                flush()
                continue
            if _FOOTER.match(line):
                continue
            if _ROW.match(line):
                flush()
                cells = cells_of(line)
                columns = [c[0] for c in cells]
                current = {"page": page_no, "cells": {"tahun": [], "negara": [], "konteks": [], "jumlah": []}}
                for (pos, txt), key in zip(cells, ("tahun", "negara", "konteks", "jumlah")):
                    current["cells"][key].append(txt)
                continue
            if current is not None:
                keys = ("tahun", "negara", "konteks", "jumlah")
                for pos, txt in cells_of(line):
                    idx = max((i for i, c in enumerate(columns) if c <= pos + 2), default=0)
                    current["cells"][keys[min(idx, 3)]].append(txt)
                continue
            if rows:
                done = True
                break
        if done:
            break
    flush()
    return rows


class Extractor(BaseExtractor):
    def extract(self) -> Iterator[Dict[str, Any]]:
        content, origin = load_pdf(
            self.http, self.config.get("url"), self.config.get("source_file"), DEFAULT_URL
        )
        rows = parse_evacuations(read_pages(content, layout=True))
        if not rows:
            raise SourceUnavailable("Renstra Dit. PWNI: evacuation table (Tahun/Negara/Jenis Kondisi/Jumlah Evacuees) not found")
        logger.info("Kemlu riwayat_evakuasi_wni: %d rows from %s", len(rows), origin)
        yield from rows
