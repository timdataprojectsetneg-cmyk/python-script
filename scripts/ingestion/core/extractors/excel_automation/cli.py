"""Excel workbook automation CLI.

python -m ingestion.core.extractors.excel_automation file.xlsx --out-dir ./out
"""

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
from .extraction import *
from .writers import *

# =============================================================================
# CLI
# =============================================================================
def parse_args():
    p = argparse.ArgumentParser(description="Excel (data + metadata) -> tabel CSV/JSON terstruktur",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("file", help="path file .xlsx")
    p.add_argument("--prefix", help="prefix nama tabel (default: dari nama sheet data)")
    p.add_argument("--const", action="append", default=[], metavar="KEY=VALUE",
                   help="kolom konstanta tambahan, boleh berulang (mis. --const provinsi=Gorontalo)")
    p.add_argument("--data-start-row", type=int, help="paksa baris awal data (1-based) bila deteksi salah")
    p.add_argument("--table-marker", action="append", default=[], metavar="TEKS",
                   help="penanda teks awal tiap tabel di dalam satu sheet (boleh berulang), "
                        "mis. --table-marker 'Tabel 1' --table-marker 'Tabel 2'")
    p.add_argument("--output", action="extend", nargs="+", metavar="NAMA",
                   help="tabel yang dikeluarkan; pisahkan dengan koma atau spasi. Pilihan: "
                        + ", ".join(OUTPUT_CHOICES) + ", all. Default: data. "
                        "Contoh: --output data,data_long,recommendation")
    p.add_argument("--format", choices=OUTPUT_FORMATS, default="csv",
                   help="format keluaran: csv (default), json (array of records), "
                        "ndjson (satu record per baris)")
    p.add_argument("--out-dir", default="./out", help="direktori keluaran (default: ./out)")
    a = p.parse_args()
    a.const_dict = {}
    for item in a.const:
        if "=" not in item:
            p.error(f"--const harus KEY=VALUE, bukan '{item}'")
        k, v = item.split("=", 1)
        a.const_dict[slugify(k)] = v
    a.outputs = parse_outputs(a.output or ["data"], p)
    return a


def _print_summary(result: ExtractionResult) -> None:
    print(f"Sheet ditemukan: {[(r.sheet, 'data') for r in result.sheets]}")
    for r in result.sheets:
        print(f"\nSheet '{r.sheet}': header baris {r.sheet_row['header_first_row']}-{r.sheet_row['header_last_row']}, "
              f"data baris {r.sheet_row['data_first_row']}-{r.sheet_row['data_last_row']}")
        print(r.wide.dtypes.astype(str).to_string())
    print("\nREKOMENDASI:")
    if result.recommendation.empty:
        print("(tidak ada)")
    else:
        print(result.recommendation[["no", "severity", "category", "target", "finding"]]
              .to_string(index=False, max_colwidth=110))
    print()


def main() -> None:
    args = parse_args()
    outputs = args.outputs
    result = extract_workbook(
        args.file,
        prefix=args.prefix,
        const=args.const_dict,
        data_start_row=args.data_start_row,
        profile="profile" in outputs,
        relations=True,
        outputs=outputs,
        table_markers=args.table_marker or None,
    )
    _print_summary(result)
    written = write_tables(result.tables, args.out_dir, args.format)
    for path in written:
        print(f"  [{args.format.upper()}] {path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:                            # noqa: BLE001
        print(f"ERROR: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        raise
