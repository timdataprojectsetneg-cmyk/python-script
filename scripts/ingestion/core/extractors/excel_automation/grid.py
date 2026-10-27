"""Excel workbook automation — grid."""

from __future__ import annotations

import argparse
import difflib
import itertools
import json
import math
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from io import BytesIO
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from .constants import *
from .utils import *

# =============================================================================
# 1. BACA SEMUA SHEET
# =============================================================================
@dataclass
class Grid:
    name: str
    values: list
    merged: list            # (r1, c1, r2, c2) 0-based inclusive

    @property
    def n_rows(self): return len(self.values)

    @property
    def n_cols(self): return len(self.values[0]) if self.values else 0

    def filled(self):
        """Salinan grid dengan sel merge diisi nilai sel kiri-atas."""
        out = [row[:] for row in self.values]
        for r1, c1, r2, c2 in self.merged:
            if r1 >= self.n_rows or c1 >= self.n_cols:
                continue
            v = self.values[r1][c1]
            for r in range(r1, min(r2, self.n_rows - 1) + 1):
                for c in range(c1, min(c2, self.n_cols - 1) + 1):
                    out[r][c] = v
        return out


def load_grids(source) -> list[Grid]:
    """Read every sheet into a Grid. ``source`` is a path or raw xlsx bytes."""
    def open_wb(data_only: bool):
        if isinstance(source, (bytes, bytearray)):
            return load_workbook(BytesIO(source), data_only=data_only)
        return load_workbook(source, data_only=data_only)

    wb_f = open_wb(False)     # untuk membaca formula
    wb_v = open_wb(True)      # nilai hasil hitung (cache)
    grids = []
    for ws_f in wb_f.worksheets:
        ws_v = wb_v[ws_f.title]
        nr, nc = ws_f.max_row, ws_f.max_column
        vals = [[ws_v.cell(r, c).value for c in range(1, nc + 1)] for r in range(1, nr + 1)]
        # Formula tanpa cache nilai (mis. '=C26') -> selesaikan referensi sederhana
        for r in range(nr):
            for c in range(nc):
                if vals[r][c] is None:
                    f = ws_f.cell(r + 1, c + 1).value
                    if isinstance(f, str) and f.startswith("="):
                        m = re.fullmatch(r"=\$?([A-Z]{1,3})\$?(\d+)", f.strip())
                        if m:
                            vals[r][c] = ws_v[f"{m.group(1)}{m.group(2)}"].value
        # pangkas baris/kolom kosong di ujung
        last_r = max((r for r in range(nr) if any(not is_blank(x) for x in vals[r])), default=-1)
        last_c = max((c for c in range(nc) if any(not is_blank(vals[r][c]) for r in range(nr))), default=-1)
        vals = [row[:last_c + 1] for row in vals[:last_r + 1]]
        merged = [(rg.min_row - 1, rg.min_col - 1, rg.max_row - 1, rg.max_col - 1)
                  for rg in ws_f.merged_cells.ranges]
        grids.append(Grid(ws_f.title, vals, merged))
    return grids


def slice_grid(g: Grid, r0: int, r1: int) -> Grid:
    """Salinan grid untuk baris ``r0..r1`` (0-based inclusive), merge disesuaikan."""
    r0, r1 = max(0, r0), min(g.n_rows - 1, r1)
    values = [row[:] for row in g.values[r0:r1 + 1]]
    merged = []
    for mr1, mc1, mr2, mc2 in g.merged:
        if mr2 < r0 or mr1 > r1:
            continue
        merged.append((max(mr1, r0) - r0, mc1, min(mr2, r1) - r0, mc2))
    return Grid(g.name, values, merged)


def _first_text(g: Grid, r: int) -> Optional[str]:
    for v in g.values[r]:
        if not is_blank(v):
            return clean_text(v)
    return None


def split_by_markers(g: Grid, markers: List[str]) -> list[tuple[Optional[str], Grid]]:
    """Pecah satu sheet menjadi beberapa tabel berdasarkan penanda baris.

    Sebuah baris dianggap awal tabel bila teks (sel non-kosong pertama) diawali
    salah satu ``markers`` (case-insensitive). Tabel membentang dari baris penanda
    sampai sebelum penanda berikutnya. Bila tidak ada penanda, kembalikan satu
    tabel berisi seluruh sheet. Label tabel = penanda yang cocok (mis. "Tabel 1").
    """
    wanted = [(m.strip(), m.strip().casefold()) for m in markers if m and m.strip()]
    starts: list[tuple[int, str]] = []
    for r in range(g.n_rows):
        txt = _first_text(g, r)
        if not txt:
            continue
        low = txt.casefold()
        hit: Optional[str] = None
        for raw, m_low in wanted:
            if low.startswith(m_low) and (hit is None or len(raw) > len(hit)):
                hit = raw
        if hit:
            starts.append((r, hit))
    if not starts:
        return [(None, g)]
    out: list[tuple[Optional[str], Grid]] = []
    for i, (r, label) in enumerate(starts):
        end = starts[i + 1][0] - 1 if i + 1 < len(starts) else g.n_rows - 1
        out.append((label, slice_grid(g, r, end)))
    return out


def detect_roles(grids: list[Grid]) -> dict[str, str]:
    roles = {g.name: ("metadata" if any(h in g.name.casefold() for h in METADATA_SHEET_HINTS) else "data")
             for g in grids}
    if "metadata" not in roles.values() and len(grids) > 1:      # tidak ada petunjuk nama
        for g in grids[1:]:
            roles[g.name] = "metadata"
    if "data" not in roles.values():
        roles[grids[0].name] = "data"
    return roles


# =============================================================================
# 2-3. HEADER, KOLOM, PATH HEADER MULTI-LEVEL
# =============================================================================
def header_paths(filled: list, hs: int, ds: int, n_cols: int) -> list[list[str]]:
    """Path header per kolom, mis. ['Jenis Kelamin', 'Laki-laki']. Menangani merge
    maupun 'center across selection' (sel kosong di kanan header induk)."""
    H = [[filled[r][c] if c < len(filled[r]) else None for c in range(n_cols)] for r in range(hs, ds)]
    for i in range(len(H)):
        for c in range(1, n_cols):
            if is_blank(H[i][c]) and not is_blank(H[i][c - 1]):
                if any(not is_blank(H[j][c]) for j in range(i + 1, len(H))):
                    H[i][c] = H[i][c - 1]
    paths = []
    for c in range(n_cols):
        parts: list[str] = []
        for i in range(len(H)):
            if not is_blank(H[i][c]):
                t = one_line(H[i][c])
                if not parts or parts[-1] != t:
                    parts.append(t)
        paths.append(parts)
    return paths


@dataclass
class Layout:
    header_start: int
    data_start: int
    data_end: int
    n_cols: int
    body_rows: list
    title_rows: list = field(default_factory=list)
    footer_rows: list = field(default_factory=list)
    dropped_rows: list = field(default_factory=list)


def detect_layout(g: Grid, data_start_override: Optional[int] = None) -> Layout:
    stats = []
    for r in range(g.n_rows):
        nb = [v for v in g.values[r] if not is_blank(v)]
        stats.append((len(nb), sum(1 for v in nb if is_numlike(v))))
    if data_start_override:
        ds = data_start_override - 1
    else:
        ds = next((r for r, (nb, nu) in enumerate(stats) if nb > 0 and nu >= 1 and nu / nb >= 0.5), None)
        if ds is None:
            raise ValueError(f"Sheet '{g.name}': tidak ditemukan baris data numerik")
    hs = next((r for r in range(ds) if stats[r][0] >= 2), ds)
    data_end = max(r for r in range(g.n_rows) if stats[r][1] >= 1)
    body, dropped = [], []
    for r in range(ds, data_end + 1):
        if stats[r][0] == 0:
            continue
        (body if stats[r][1] >= 1 else dropped).append(r)
    footer = [r for r in range(data_end + 1, g.n_rows) if stats[r][0] > 0]
    title = [r for r in range(hs) if stats[r][0] > 0]
    n_cols = max(c for r in range(hs, data_end + 1) for c in range(g.n_cols) if not is_blank(g.values[r][c])) + 1
    return Layout(hs, ds, data_end, n_cols, body, title, footer, dropped)


def name_columns(paths, roles, letters) -> list[str]:
    n = len(paths)
    names: list[Optional[str]] = [None] * n
    i = 0
    while i < n:
        if roles[i] == "label":
            j = i
            while j + 1 < n and roles[j + 1] == "label" and paths[j + 1] == paths[i]:
                j += 1
            base = shorten_name(paths[i]) if paths[i] else f"col_{letters[i].lower()}"
            for k, c in enumerate(range(i, j + 1)):
                names[c] = base if k == 0 else (LEVEL_NAMES[k] if k < len(LEVEL_NAMES) else f"level_{k + 1}")
            i = j + 1
        else:
            names[i] = shorten_name(paths[i]) if paths[i] else f"col_{letters[i].lower()}"
            i += 1
    return dedupe([n_ or "col" for n_ in names])
