"""Excel workbook automation — writers."""

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

def write_csvs(tables: Dict[str, pd.DataFrame], out_dir: str) -> List[str]:
    """Tulis setiap tabel ke CSV (UTF-8 BOM, tanpa index). Kembalikan path yang ditulis."""
    os.makedirs(out_dir, exist_ok=True)
    written: List[str] = []
    for name, df in tables.items():
        path = os.path.join(out_dir, f"{name}.csv")
        df.to_csv(path, index=False, encoding="utf-8-sig")
        written.append(path)
    return written


def _py_scalar(value: Any) -> Any:
    """Convert a pandas/numpy scalar to a JSON/pydantic-friendly Python value."""
    if value is None or value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if math.isnan(float(value)) else float(value)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    return value


def to_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """DataFrame -> list of dict (NaN/NaT -> None, tipe numpy -> Python native)."""
    return [{key: _py_scalar(value) for key, value in row.items()} for row in df.to_dict(orient="records")]


def tables_to_records(tables: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict[str, Any]]]:
    """Semua tabel -> ``{nama_tabel: [record, ...]}`` untuk normalisasi/loader."""
    return {name: to_records(df) for name, df in tables.items()}




def write_tables(tables: Dict[str, pd.DataFrame], out_dir: str, fmt: str = "csv") -> List[str]:
    """Tulis tabel ke disk. ``fmt``: csv, json (array of records), atau ndjson."""
    fmt = (fmt or "csv").lower()
    if fmt == "csv":
        return write_csvs(tables, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    written: List[str] = []
    for name, df in tables.items():
        records = to_records(df)
        if fmt == "json":
            path = os.path.join(out_dir, f"{name}.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(records, handle, ensure_ascii=False, indent=2, default=str)
        else:
            path = os.path.join(out_dir, f"{name}.ndjson")
            with open(path, "w", encoding="utf-8") as handle:
                for record in records:
                    handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        written.append(path)
    return written
