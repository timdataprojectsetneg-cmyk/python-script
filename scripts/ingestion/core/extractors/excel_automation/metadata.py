"""Excel workbook automation — metadata."""

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
from .grid import Grid, header_paths

# =============================================================================
# 5-6. METADATA (STANDAR DATA & METADATA)
# =============================================================================
@dataclass
class Metadata:
    dataset: pd.DataFrame
    indicator: Optional[pd.DataFrame]
    indicator_paths: dict
    indicator_letters: dict
    klasifikasi: list
    info: dict


def parse_kv_block(g: Grid, end_row: int) -> list[dict]:
    rows, section = [], None

    def add(key, value, r, c):
        rows.append(dict(sheet_name=g.name, section=section, key=key, value=value,
                         source_cell=f"{get_column_letter(c + 1)}{r + 1}"))

    for r in range(end_row):
        cells = [(c, v) for c, v in enumerate(g.values[r]) if not is_blank(v)]
        if not cells:
            continue
        c0, v0 = cells[0]
        if len(cells) == 1 and c0 == 0 and isinstance(v0, str) and not kv_from_text(v0):
            section = clean_text(v0)
            continue
        consumed = set()
        if c0 == 0 and isinstance(v0, str) and not kv_from_text(v0):
            label, val = clean_text(v0), None
            for c, v in cells[1:]:
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    continue                                   # nomor urut kolom
                if isinstance(v, str) and kv_from_text(v):
                    break
                val = (c, v)
                break
            consumed.add(0)
            if val is not None:
                add(label, str(val[1]).strip(), r, val[0]); consumed.add(val[0])
            elif not label.startswith("("):
                add(label, None, r, 0)
        for c, v in cells:
            if c in consumed or not isinstance(v, str):
                continue
            kv = kv_from_text(v)
            if kv:
                add(kv[0], kv[1], r, c)
    return rows


def parse_metadata(g: Grid) -> tuple[Metadata, dict]:
    filled = g.filled()
    # --- cari tabel indikator: baris yang memuat sel 'No.' ---
    hr = None
    for r in range(g.n_rows):
        txt = [clean_text(v).casefold() for v in g.values[r] if isinstance(v, str)]
        if any(t in ("no.", "no") for t in txt) and sum(not is_blank(v) for v in g.values[r]) >= 4:
            hr = r
            break
    kv_rows = parse_kv_block(g, hr if hr is not None else g.n_rows)

    indicator, ind_paths, ind_letters, ind_info = None, {}, {}, {}
    if hr is not None:
        code_r = None
        for r in range(hr + 1, min(hr + 7, g.n_rows)):
            nb = [v for v in g.values[r] if not is_blank(v)]
            if len(nb) >= 4 and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                                    and float(v).is_integer() for v in nb):
                code_r = r
                break
        ds = (code_r + 1) if code_r is not None else hr + 1
        n_cols = g.n_cols
        paths = header_paths(filled, hr, code_r if code_r is not None else hr + 1, n_cols)
        names = dedupe([shorten_name(p) if p else f"col_{get_column_letter(i + 1).lower()}"
                        for i, p in enumerate(paths)])
        data = []
        for r in range(ds, g.n_rows):
            row = g.values[r]
            if all(is_blank(v) for v in row):
                break
            data.append(row)
        cols = {}
        for i, nm in enumerate(names):
            vals = [None if is_blank(row[i]) else (row[i].strip() if isinstance(row[i], str) else row[i])
                    for row in data]
            dt = infer_dtype(vals)
            cols[nm] = to_series([str(v) if (dt == "text" and v is not None) else v for v in vals], dt)
        indicator = pd.DataFrame(cols)
        ind_paths = {nm: paths[i] for i, nm in enumerate(names)}
        ind_letters = {nm: get_column_letter(i + 1) for i, nm in enumerate(names)}
        ind_info = dict(header_first=hr + 1, header_last=(code_r if code_r is not None else hr + 1),
                        data_first=ds + 1, data_last=ds + len(data), n_indicators=len(data))

    ds_df = pd.DataFrame(kv_rows)
    if ds_df.empty:
        ds_df = pd.DataFrame(columns=["sheet_name", "section", "key", "value", "source_cell"])
    ds_df.insert(len(ds_df.columns), "ordinal", range(1, len(ds_df) + 1))

    # daftar klasifikasi (dari kunci 'Klasifikasi' dan kolom klasifikasi di tabel indikator)
    texts = [str(v) for k, v in zip(ds_df["key"], ds_df["value"]) if str(k).casefold() == "klasifikasi" and v]
    if indicator is not None and "klasifikasi" in indicator.columns:
        texts += [str(v) for v in indicator["klasifikasi"].dropna()]
    klas, seen = [], set()
    for t in texts:
        for line in t.split("\n"):
            item = re.sub(r"^\s*\d+[.)]\s*", "", line).strip()
            if item and item.casefold() not in seen:
                seen.add(item.casefold()); klas.append(item)

    info = dict(ind_info, n_kv=len(ds_df), n_klasifikasi=len(klas))
    return Metadata(ds_df, indicator, ind_paths, ind_letters, klas, info), info


def indicator_info(meta: Metadata, col_path: list[str]) -> dict:
    out = dict(nama=None, definisi=None, ukuran=None, satuan=None, interpretasi=None, source=None)
    ind = meta.indicator

    def pick(row, *keys):
        for c in ind.columns:
            if any(c == k or c.startswith(k) for k in keys):
                v = row[c]
                return None if pd.isna(v) else str(v)
        return None

    if ind is not None and len(ind):
        row = None
        if len(ind) == 1:
            row = ind.iloc[0]
        else:
            best, bs = None, 0.0
            for _, rw in ind.iterrows():
                s = text_score(" ".join(col_path), pick(rw, "nama_indikator") or "")[0]
                if s > bs:
                    best, bs = rw, s
            if bs >= MATCH_THRESHOLD:
                row = best
        if row is not None:
            out.update(nama=pick(row, "nama_indikator"), definisi=pick(row, "definisi"),
                       ukuran=pick(row, "ukuran"), satuan=pick(row, "satuan"),
                       interpretasi=pick(row, "interpretasi"),
                       source="metadata: tabel indikator")
            return out
    kv = {str(k).casefold(): v for k, v in zip(meta.dataset["key"], meta.dataset["value"]) if v}
    if kv:
        out.update(nama=kv.get("judul data") or kv.get("konsep"), definisi=kv.get("definisi"),
                   ukuran=kv.get("ukuran"), satuan=kv.get("satuan"),
                   source="metadata: blok Standar Data")
    return out


def describe_measure(info: dict, path: list[str]) -> tuple[Optional[str], Optional[str], Optional[str]]:
    if not any(info.get(k) for k in ("nama", "ukuran", "satuan")):
        return None, None, None
    parts = [info["nama"]] if info.get("nama") else []
    if path:
        parts.append("kolom: " + " > ".join(path))
    if info.get("ukuran"):
        parts.append(f"ukuran: {info['ukuran']}")
    if info.get("satuan"):
        parts.append(f"satuan: {info['satuan']}")
    return " | ".join(parts), info.get("definisi"), info.get("source")


# --- pencocokan nama dimensi di data <-> daftar klasifikasi di metadata ---
def _norm(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def tokens(text: str) -> set:
    toks = set()
    for w in re.findall(r"[a-z]+", _norm(text)):
        if w in STOPWORDS:
            continue
        toks.add(w)
        if w in SYNONYMS:
            toks |= set(SYNONYMS[w].split())
    return toks


def text_score(src: str, cand: str) -> tuple[float, str]:
    a, b = tokens(src), tokens(cand)
    if not a or not b:
        return 0.0, "none"
    if " ".join(sorted(a)) == " ".join(sorted(b)):
        return 1.0, "exact"
    inter = len(a & b)
    contain, jacc = inter / len(b), inter / len(a | b)
    seq = difflib.SequenceMatcher(None, _norm(src), _norm(cand)).ratio()
    return max(0.7 * contain + 0.3 * jacc, seq), "token_overlap"


def match_dimension(src: str, klasifikasi: list[str]) -> tuple[Optional[str], float, str]:
    best, bs, bm = None, 0.0, "none"
    for k in klasifikasi:
        s, m = text_score(src, k)
        if s > bs:
            best, bs, bm = k, s, m
    if bs < MATCH_THRESHOLD:
        return None, round(bs, 3), "none"
    return best, round(bs, 3), bm
