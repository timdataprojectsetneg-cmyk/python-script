"""Excel workbook automation — utils."""

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
from .constants import _RE_EN, _RE_ID, _RE_PLAIN, KV_RE, RE_ISO_DATE, RE_ISO_TS

def is_blank(v: Any) -> bool:
    return v is None or (isinstance(v, str) and v.replace("\xa0", " ").strip() == "")


def clean_text(v: Any) -> str:
    return re.sub(r"\s+", " ", str(v).replace("\xa0", " ")).strip()


def one_line(v: Any) -> str:
    """Baris pertama sel (header sering berisi catatan di baris berikutnya)."""
    return clean_text(str(v).replace("\xa0", " ").split("\n")[0])


def slugify(text: Any, maxlen: int = MAX_IDENT) -> str:
    s = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower() or "col"
    if s[0].isdigit():
        s = "c_" + s
    return s[:maxlen].rstrip("_")


def shorten_name(parts: list[str], maxlen: int = MAX_IDENT) -> str:
    """Slug dari path header; bila terlalu panjang buang level paling atas satu per satu."""
    for k in range(len(parts)):
        cand = slugify(" ".join(parts[k:]), maxlen=200)
        if len(cand) <= maxlen:
            return cand
    return slugify(parts[-1], maxlen) if parts else "col"


def dedupe(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    out = []
    for n in names:
        if n in seen:
            seen[n] += 1
            n = f"{n[:MAX_IDENT - 4]}_{seen[n]}"
        else:
            seen[n] = 1
        out.append(n)
    # pastikan unik setelah suffix
    final, used = [], set()
    for n in out:
        base, i = n, 2
        while n in used:
            n = f"{base}_{i}"; i += 1
        used.add(n); final.append(n)
    return final


def parse_number(v: Any):
    """Return int/float, None (kosong), DASH, atau NOT_NUM."""
    if v is None:
        return None
    if isinstance(v, bool):
        return NOT_NUM
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        if np.isnan(v):
            return None
        return int(v) if float(v).is_integer() else float(v)
    if isinstance(v, (datetime, date)):
        return NOT_NUM
    s = str(v).replace("\xa0", " ").strip()
    if s == "":
        return None
    if re.fullmatch(r"[-–—\s]+", s):
        return DASH
    if s.casefold() in NULL_TOKENS:
        return None
    s2 = s.replace(" ", "")
    if _RE_ID.match(s2):
        s2 = s2.replace(".", "").replace(",", ".")
    elif _RE_EN.match(s2):
        s2 = s2.replace(",", "")
    elif _RE_PLAIN.match(s2):
        s2 = s2.replace(",", ".")
    else:
        return NOT_NUM
    try:
        f = float(s2)
    except ValueError:
        return NOT_NUM
    return int(f) if (f.is_integer() and "." not in s2) else f


def is_numlike(v: Any) -> bool:
    r = parse_number(v)
    return r is not None and r is not NOT_NUM


def infer_dtype(values) -> str:
    vals = [v for v in values if v is not None and not (isinstance(v, float) and np.isnan(v))]
    if not vals:
        return "text"
    if all(isinstance(v, bool) for v in vals):
        return "boolean"
    if any(isinstance(v, bool) for v in vals):
        return "text"
    if all(isinstance(v, (datetime, date)) for v in vals):
        has_time = any(isinstance(v, datetime) and (v.hour or v.minute or v.second) for v in vals)
        return "timestamp" if has_time else "date"
    if all(isinstance(v, (int, np.integer)) for v in vals):
        return "bigint"
    if all(isinstance(v, (int, float, np.integer, np.floating)) for v in vals):
        return "numeric"
    if all(isinstance(v, str) for v in vals):
        if all(RE_ISO_DATE.fullmatch(v.strip()) for v in vals):
            return "date"
        if all(RE_ISO_TS.fullmatch(v.strip()) for v in vals):
            return "timestamp"
    return "text"


def _null(v) -> bool:
    if v is None or v is pd.NA or v is pd.NaT:
        return True
    return isinstance(v, (float, np.floating)) and bool(np.isnan(v))


def to_series(values, dtype: str):
    values = [None if _null(v) else v for v in values]
    if dtype == "bigint":
        return pd.array([None if v is None else int(v) for v in values], dtype="Int64")
    if dtype == "numeric":
        return pd.Series([np.nan if v is None else float(v) for v in values], dtype="float64")
    if dtype == "boolean":
        return pd.array([None if v is None else bool(v) for v in values], dtype="boolean")
    if dtype == "date":
        s = pd.to_datetime(pd.Series(values), errors="coerce")
        return pd.Series([None if pd.isna(x) else x.date() for x in s], dtype="object")
    if dtype == "timestamp":
        return pd.to_datetime(pd.Series(values), errors="coerce")
    return pd.Series([None if v is None else str(v) for v in values], dtype="object")


def kv_from_text(text: Any):
    m = KV_RE.match(str(text))
    return (m.group(1).strip(), m.group(2).strip()) if m else None
