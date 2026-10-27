"""Excel workbook automation — extraction."""

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
from .grid import *
from .metadata import *
from .tables import *

def parse_outputs(values, parser=None) -> list[str]:
    """['data,data_long', '_profile'] -> ['data', 'data_long', 'profile'] (urutan tetap, tanpa duplikat)."""
    out: list[str] = []
    for chunk in values:
        for tok in re.split(r"[,\s]+", chunk):
            name = tok.strip().lower().lstrip("_")
            if not name:
                continue
            if name == "all":
                return list(OUTPUT_CHOICES)
            name = OUTPUT_ALIASES.get(name, name)
            if name not in OUTPUT_CHOICES:
                msg = f"output '{tok}' tidak dikenal. Pilihan: {', '.join(OUTPUT_CHOICES)}, all"
                if parser is not None:
                    parser.error(msg)
                raise ValueError(msg)
            if name not in out:
                out.append(name)
    return out


# =============================================================================
# API REUSABLE: BACA WORKBOOK -> TABEL (DICT DATAFRAME)
# =============================================================================
@dataclass
class ExtractionResult:
    """Hasil otomasi membaca Excel: tabel siap CSV untuk normalisasi & loaders."""
    tables: Dict[str, pd.DataFrame]
    prefix: str
    recommendation: pd.DataFrame
    sheets: List[SheetResult]
    metadata: Metadata


def extract_workbook(
    source: "str | bytes",
    *,
    prefix: Optional[str] = None,
    const: Optional[Dict[str, str]] = None,
    data_start_row: Optional[int] = None,
    profile: bool = True,
    relations: bool = True,
    outputs: Optional[List[str]] = None,
    table_markers: Optional[List[str]] = None,
) -> ExtractionResult:
    """Baca workbook Excel dan kembalikan tabel terstruktur (DataFrame).

    Args:
        source: path file .xlsx, atau bytes dari file .xlsx (mis. hasil unduhan).
        prefix: prefix nama tabel; default dari nama sheet data.
        const: kolom konstanta tambahan, mis. {"provinsi": "Gorontalo"}.
        data_start_row: paksa baris awal data (1-based) bila deteksi salah.
        profile: hitung tabel profiling.
        relations: hitung tabel relasi (dipakai untuk deteksi kunci).
        outputs: batasi tabel keluaran (lihat OUTPUT_CHOICES). None = semua.
        table_markers: penanda teks awal tiap tabel di dalam satu sheet, mis.
            ["Tabel 1", "Tabel 2"]. Bila diisi, tiap sheet dipecah menjadi beberapa
            tabel per penanda; bila kosong, satu tabel per sheet (perilaku lama).

    Returns:
        ExtractionResult dengan ``.tables`` berisi ``{nama_tabel: DataFrame}``.
    """
    const_dict = {slugify(k): v for k, v in (const or {}).items()}
    source_name = os.path.basename(source) if isinstance(source, (str, os.PathLike)) else "<bytes>"
    opts = ExtractionOptions(file=source_name, prefix=prefix, const=const_dict,
                             data_start_row=data_start_row, profile=profile, relations=relations,
                             table_markers=table_markers)

    # 1. baca semua sheet
    grids = load_grids(source)
    roles = detect_roles(grids)
    data_grids = [g for g in grids if roles[g.name] == "data"]
    meta_grids = [g for g in grids if roles[g.name] == "metadata"]
    resolved_prefix = prefix or slugify(data_grids[0].name, 40)

    # 5-6. metadata
    meta = Metadata(pd.DataFrame(columns=["sheet_name", "section", "key", "value", "source_cell", "ordinal"]),
                    None, {}, {}, [], {})
    sheet_rows = []
    for mg in meta_grids:
        meta, info = parse_metadata(mg)
        sheet_rows.append(dict(sheet_name=mg.name, role="metadata", n_rows=mg.n_rows, n_cols=mg.n_cols,
                               n_merged_ranges=len(mg.merged),
                               header_first_row=info.get("header_first"), header_last_row=info.get("header_last"),
                               data_first_row=info.get("data_first"), data_last_row=info.get("data_last"),
                               label_columns=None, measure_columns=None,
                               notes=f"{info.get('n_kv', 0)} pasangan key-value; {info.get('n_indicators', 0)} indikator; "
                                     f"{info.get('n_klasifikasi', 0)} klasifikasi"))
        break                                           # satu sheet metadata dipakai

    # 2-4, 7-9. sheet data
    skipped: list[dict] = []
    if table_markers:
        units: list[tuple[Optional[str], Grid]] = []
        for g in data_grids:
            units.extend(split_by_markers(g, table_markers))
        multi = len(units) > 1
        results = []
        seen: dict[tuple[str, str], int] = {}
        for label, sub in units:
            key = (sub.name, slugify(label or ""))
            seen[key] = seen.get(key, 0) + 1
            if seen[key] > 1:                       # nama tabel harus unik
                label = f"{label or sub.name}_{seen[key]}"
            try:
                results.append(process_data_sheet(sub, meta, opts, resolved_prefix, multi, table_label=label))
            except ValueError as exc:
                skipped.append(dict(
                    sheet_name=sub.name, category="struktur", severity="warn", target=str(label),
                    finding=f"Segmen tabel dilewati: {exc}",
                    recommendation="Pastikan penanda menunjuk tabel data (punya kolom label & ukuran), "
                                   "atau hapus penanda ini."))
    else:
        results = [process_data_sheet(g, meta, opts, resolved_prefix, len(data_grids) > 1)
                   for g in data_grids]
    sheet_rows = [r.sheet_row for r in results] + sheet_rows

    # --- susun tabel keluaran ---
    tables: Dict[str, pd.DataFrame] = {}
    colmeta_all = [cm for r in results for cm in r.colmeta]
    if meta.indicator is not None:                      # kolom meta_indicator (nama asli header disimpan)
        for i, c in enumerate(meta.indicator.columns, 1):
            dt = infer_dtype(meta.indicator[c].dropna().tolist())
            colmeta_all.append(dict(sheet_name=meta_grids[0].name, table_name=f"{resolved_prefix}_meta_indicator",
                                    column_name=c, ordinal_position=i, column_role="metadata",
                                    source_col=meta.indicator_letters[c], header_path=" > ".join(meta.indicator_paths[c]),
                                    inferred_type=dt, pg_type=PG_NAMES[dt],
                                    description=" > ".join(meta.indicator_paths[c]), definition=None,
                                    metadata_match=None, match_score=None, description_source="header sheet metadata"))
    meta_col_df = pd.DataFrame(colmeta_all)
    meta_col_df["match_score"] = pd.to_numeric(meta_col_df["match_score"])
    meta_col_df["ordinal_position"] = pd.array(meta_col_df["ordinal_position"], dtype="Int64")

    for r in results:
        tables[r.table_wide] = r.wide
        if r.long is not None:
            tables[r.table_long] = r.long
    tables[f"{resolved_prefix}_dim_mapping"] = pd.concat([r.dim_mapping for r in results], ignore_index=True)
    tables[f"{resolved_prefix}_meta_sheet"] = pd.DataFrame(sheet_rows)
    tables[f"{resolved_prefix}_meta_dataset"] = meta.dataset
    if meta.indicator is not None:
        tables[f"{resolved_prefix}_meta_indicator"] = meta.indicator
    tables[f"{resolved_prefix}_meta_column"] = meta_col_df
    if profile:
        tables[f"{resolved_prefix}_profile"] = pd.concat([r.profile for r in results], ignore_index=True)
    if relations:
        tables[f"{resolved_prefix}_relation"] = pd.concat([r.relation for r in results], ignore_index=True)
    rec_df = pd.DataFrame([x for r in results for x in r.recs] + skipped)
    sev = {"high": 0, "warn": 1, "info": 2}
    if not rec_df.empty:
        rec_df = rec_df.sort_values("severity", key=lambda s: s.map(sev), kind="stable").reset_index(drop=True)
        rec_df.insert(0, "no", range(1, len(rec_df) + 1))
    tables[f"{resolved_prefix}_recommendation"] = rec_df

    # outputs: sisakan hanya tabel yang diminta
    if outputs is not None:
        keep = set()
        for name in outputs:
            if name == "data":
                keep |= {r.table_wide for r in results}
            elif name == "data_long":
                keep |= {r.table_long for r in results}
            else:
                keep.add(f"{resolved_prefix}_{name}")
        tables = {k: v for k, v in tables.items() if k in keep}

    return ExtractionResult(tables=tables, prefix=resolved_prefix, recommendation=rec_df,
                            sheets=results, metadata=meta)
