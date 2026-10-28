"""Excel workbook automation — analysis."""

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

# =============================================================================
# 7-8. PROFILING & RELASI
# =============================================================================
def profile_df(sheet, table, df, cols, dtypes, extra) -> pd.DataFrame:
    rows = []
    for c in cols:
        s = df[c]
        n = len(s)
        nn = int(s.isna().sum())
        d = dict(sheet_name=sheet, table_name=table, column_name=c, inferred_type=dtypes[c],
                 n_rows=n, n_null=nn, null_pct=round(100 * nn / n, 2) if n else None,
                 n_distinct=int(s.nunique(dropna=True)))
        nz = s.dropna()
        if dtypes[c] in ("bigint", "numeric") and len(nz):
            f = nz.astype(float)
            d.update(min_value=str(nz.min()), max_value=str(nz.max()), mean_value=f.mean(),
                     median_value=f.median(), std_value=f.std(), sum_value=f.sum())
        elif len(nz):
            st = nz.astype(str)
            vc = st.value_counts()
            d.update(min_value=st.min(), max_value=st.max(), top_value=vc.index[0], top_freq=int(vc.iloc[0]),
                     min_len=int(st.str.len().min()), max_len=int(st.str.len().max()))
        d.update(extra.get(c, {}))
        rows.append(d)
    out = pd.DataFrame(rows)
    for c in ("mean_value", "median_value", "std_value", "sum_value"):
        if c not in out:
            out[c] = np.nan
        out[c] = pd.to_numeric(out[c])
    for c in ("top_freq", "min_len", "max_len", "dash_cells"):
        if c not in out:
            out[c] = None
        out[c] = pd.array(out[c], dtype="Int64")
    return out


def analyze_relations(sheet, df, label_cols, measure_cols, paths, is_total_row_col="is_total_row"):
    rel = []

    def add(rtype, left, right, expr, checked=None, passed=None, failed=None, status="info",
            detail=None, value=None):
        rel.append(dict(sheet_name=sheet, relation_type=rtype, left_scope=left, right_scope=right,
                        expression=expr, checked=checked, passed=passed, failed=failed,
                        status=status, detail=detail, value=value))

    n = len(df)
    # R1. kandidat kunci
    key = None
    for k in range(1, len(label_cols) + 1):
        for combo in itertools.combinations(label_cols, k):
            sub = df[list(combo)]
            if not sub.isna().any().any() and not sub.duplicated().any():
                key = list(combo)
                break
        if key:
            break
    if key:
        add("candidate_key", ", ".join(key), "(seluruh kolom)", f"UNIQUE({', '.join(key)})", n, n, 0, "ok",
            "Kombinasi unik dan tidak ada NULL -> layak jadi primary key")
    else:
        add("candidate_key", ", ".join(label_cols), "(seluruh kolom)", "UNIQUE(label_cols)", n, None, None,
            "warn", "Tidak ada kombinasi kolom label yang unik")

    # R2. hierarki antar kolom label
    for p, c in zip(label_cols[:-1], label_cols[1:]):
        per_child = df.groupby(c)[p].nunique()
        multi = per_child[per_child > 1]
        det = (f"{df[p].nunique()} nilai '{p}' x {df[c].nunique()} nilai '{c}' berbeda"
               + (f"; nilai '{c}' yang muncul di >1 '{p}': {', '.join(map(str, multi.index[:5]))}"
                  f"{' ...' if len(multi) > 5 else ''}" if len(multi) else ""))
        add("hierarchy", p, c, f"{p} 1..n {c}", df[p].nunique(), None, None, "info", det)

    # R3. Total kolom = jumlah kolom lain dalam grup header yang sama
    groups: dict = {}
    for c in measure_cols:
        groups.setdefault(tuple(paths[c][:-1]), []).append(c)
    for parent, cols in groups.items():
        tot = [c for c in cols if paths[c] and paths[c][-1].casefold() in TOTAL_LABELS]
        oth = [c for c in cols if c not in tot]
        if len(tot) == 1 and len(oth) >= 2:
            lhs = df[tot[0]].astype(float).fillna(0)
            rhs = df[oth].astype(float).fillna(0).sum(axis=1)
            ok = np.isclose(lhs, rhs, rtol=0, atol=1e-6)
            bad = ([" / ".join(map(str, row)) for row in df.loc[~ok, label_cols].head(5).itertuples(index=False)]
                   if not ok.all() else [])
            add("sum_columns", tot[0], ", ".join(oth), f"{tot[0]} = " + " + ".join(oth), n, int(ok.sum()),
                int((~ok).sum()), "ok" if ok.all() else "mismatch",
                None if ok.all() else "Baris tidak cocok: " + "; ".join(bad))

    # R4. Subtotal baris: SUM(baris non-total) = baris Total, per dimensi
    if is_total_row_col in df and df[is_total_row_col].any():
        dim = label_cols[0] if len(label_cols) >= 2 else None
        gb = df.groupby(dim, sort=False) if dim else [(None, df)]
        for c in measure_cols:
            checked = passed = 0
            bad = []
            for d, sub in gb:
                tot_rows = sub[sub[is_total_row_col]]
                if len(tot_rows) != 1 or sub[is_total_row_col].all():
                    continue
                s = float(sub.loc[~sub[is_total_row_col], c].astype(float).fillna(0).sum())
                t = float(tot_rows[c].astype(float).fillna(0).iloc[0])
                checked += 1
                if abs(s - t) <= 1e-6:
                    passed += 1
                else:
                    bad.append(f"{d}: jumlah baris={s:,.0f} vs Total={t:,.0f}")
            if checked:
                add("sum_rows", c, dim or "(tabel)", f"SUM(baris non-total) = baris Total, per {dim or 'tabel'}",
                    checked, passed, checked - passed, "ok" if passed == checked else "mismatch",
                    None if not bad else "; ".join(bad[:5]))

        # R5. Konsistensi grand total antar dimensi
        for c in measure_cols:
            vals = df.loc[df[is_total_row_col], c].dropna().unique()
            add("grand_total_consistency", c, "(semua dimensi)", "baris Total sama di semua dimensi",
                int(df[is_total_row_col].sum()), None, None, "ok" if len(vals) == 1 else "mismatch",
                f"{len(vals)} nilai Total berbeda: {', '.join(f'{v:,.0f}' for v in vals[:5])}")

    # R6. Korelasi antar kolom ukuran (non-total)
    non_total_cols = [c for c in measure_cols if not (paths[c] and paths[c][-1].casefold() in TOTAL_LABELS)]
    if len(non_total_cols) >= 2:
        body = df.loc[~df[is_total_row_col]] if is_total_row_col in df else df
        for a, b in itertools.combinations(non_total_cols, 2):
            r = body[[a, b]].astype(float).corr().iloc[0, 1]
            add("correlation", a, b, "pearson r (baris non-total)", len(body), None, None, "info",
                "Korelasi antar kolom ukuran", None if pd.isna(r) else round(float(r), 4))
    return pd.DataFrame(rel)
