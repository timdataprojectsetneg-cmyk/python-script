"""Excel workbook automation — tables."""

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
from .analysis import *

# =============================================================================
# PEMROSESAN SHEET DATA
# =============================================================================
@dataclass
class SheetResult:
    sheet: str
    table_wide: str
    table_long: Optional[str]
    wide: pd.DataFrame
    long: Optional[pd.DataFrame]
    dtypes_wide: dict
    dtypes_long: dict
    colmeta: list
    profile: Optional[pd.DataFrame]
    relation: Optional[pd.DataFrame]
    dim_mapping: pd.DataFrame
    recs: list
    sheet_row: dict
    pk_wide: list
    pk_long: list


@dataclass
class ExtractionOptions:
    """Opsi yang mengendalikan pemrosesan sheet data (pengganti argumen CLI)."""
    file: str
    prefix: Optional[str] = None
    const: Dict[str, str] = field(default_factory=dict)
    data_start_row: Optional[int] = None
    profile: bool = True
    relations: bool = True
    table_markers: Optional[List[str]] = None


def process_data_sheet(g: Grid, meta: Metadata, opts: ExtractionOptions, prefix: str, multi: bool,
                       table_label: Optional[str] = None) -> SheetResult:
    table_slug = f"{slugify(g.name)}_{slugify(table_label)}" if table_label else slugify(g.name)
    t_wide = f"{prefix}_{table_slug}_data" if multi else f"{prefix}_data"
    t_long = f"{prefix}_{table_slug}_data_long" if multi else f"{prefix}_data_long"
    filled = g.filled()
    L = detect_layout(g, opts.data_start_row)
    n_cols = L.n_cols
    letters = [get_column_letter(c + 1) for c in range(n_cols)]
    paths = header_paths(filled, L.header_start, L.data_start, n_cols)
    recs: list[dict] = []

    def rec(cat, sev, target, finding, reco):
        recs.append(dict(sheet_name=g.name, category=cat, severity=sev, target=target,
                         finding=finding, recommendation=reco))

    # --- peran kolom: label vs ukuran ---
    roles = []
    for c in range(n_cols):
        nb = [g.values[r][c] for r in L.body_rows if not is_blank(g.values[r][c])]
        nu = sum(1 for v in nb if is_numlike(v))
        roles.append("measure" if nb and nu / len(nb) >= 0.8 else "label")
    names = name_columns(paths, roles, letters)
    label_idx = [c for c in range(n_cols) if roles[c] == "label"]
    meas_idx = [c for c in range(n_cols) if roles[c] == "measure"]
    if not label_idx or not meas_idx:
        raise ValueError(f"Sheet '{g.name}': tidak ditemukan pasangan kolom label & ukuran")
    label_cols = [names[c] for c in label_idx]
    meas_cols = [names[c] for c in meas_idx]
    path_of = {names[c]: paths[c] for c in range(n_cols)}
    letter_of = {names[c]: letters[c] for c in range(n_cols)}

    # --- kolom label: bersihkan, isi sel merge, forward fill ---
    n_merge_filled = n_ws = n_ffill = 0
    lab: dict[str, list] = {}
    for c in label_idx:
        vals = []
        for r in L.body_rows:
            raw, fv = g.values[r][c], filled[r][c]
            if is_blank(raw) and not is_blank(fv):
                n_merge_filled += 1
            t = None if is_blank(fv) else clean_text(fv)
            if not is_blank(raw) and str(raw) != t:
                n_ws += 1
            vals.append(t)
        lab[names[c]] = vals
    lab_df = pd.DataFrame(lab)
    if len(label_cols) > 1:
        before = lab_df[label_cols[:-1]].isna().sum().sum()
        lab_df[label_cols[:-1]] = lab_df[label_cols[:-1]].ffill()
        n_ffill = int(before - lab_df[label_cols[:-1]].isna().sum().sum())

    # --- kolom ukuran: parse angka ---
    meas: dict[str, list] = {}
    dash_cells: dict[str, int] = {}
    nonnum: list[str] = []
    for c in meas_idx:
        vals, nd = [], 0
        for r in L.body_rows:
            p = parse_number(g.values[r][c])
            if p is DASH:
                nd += 1
                p = 0 if DASH_AS_ZERO else None
            elif p is NOT_NUM:
                nonnum.append(f"{letters[c]}{r + 1}={g.values[r][c]!r}")
                p = None
            vals.append(p)
        meas[names[c]] = vals
        dash_cells[names[c]] = nd

    # --- tipe data ---
    dtypes = {c: "text" for c in label_cols}
    for c in meas_cols:
        dtypes[c] = infer_dtype(meas[c])

    # --- konstanta (--const) & lineage ---
    const_cols = list(opts.const.keys())
    now = datetime.now().replace(microsecond=0)
    n = len(L.body_rows)
    wide = {c: to_series(lab_df[c].tolist(), "text") for c in label_cols}
    for c in meas_cols:
        wide[c] = to_series(meas[c], dtypes[c])
    is_total_row = [any(isinstance(v, str) and v.casefold() in TOTAL_LABELS for v in row)
                    for row in lab_df[label_cols].itertuples(index=False)]
    wide["is_total_row"] = pd.array(is_total_row, dtype="boolean")
    for k, v in opts.const.items():
        wide[k] = pd.Series([v] * n, dtype="object")
    wide["_source_row"] = pd.array([r + 1 for r in L.body_rows], dtype="Int64")
    wide["_sheet_name"] = pd.Series([g.name] * n, dtype="object")
    wide["_source_file"] = pd.Series([os.path.basename(opts.file)] * n, dtype="object")
    wide["_loaded_at"] = pd.Series([now] * n)
    wide_df = pd.DataFrame(wide)
    dtypes.update({"is_total_row": "boolean", "_source_row": "bigint", "_sheet_name": "text",
                   "_source_file": "text",
                   "_loaded_at": "timestamp", **{k: "text" for k in const_cols}})
    wide_df["is_total_row"] = wide_df["is_total_row"].astype(bool)

    # --- pemetaan dimensi <-> metadata (langkah 5) ---
    klas = meta.klasifikasi
    dm_rows = []
    dim_src = label_cols[0]
    for v in pd.unique(wide_df[dim_src].dropna()):
        m, s, how = match_dimension(v, klas)
        cnt = wide_df.loc[wide_df[dim_src] == v]
        dm_rows.append(dict(sheet_name=g.name, source_level=f"baris:{dim_src}", source_value=v,
                            matched_klasifikasi=m, score=s, method=how,
                            n_categories=int((~cnt["is_total_row"]).sum()),
                            has_total_row=bool(cnt["is_total_row"].any())))
    parents = {}
    for c in meas_cols:
        if len(path_of[c]) >= 2:
            parents.setdefault(" > ".join(path_of[c][:-1]), []).append(c)
    for p, cols in parents.items():
        m, s, how = match_dimension(p.split(" > ")[-1], klas)
        dm_rows.append(dict(sheet_name=g.name, source_level="header:kolom", source_value=p,
                            matched_klasifikasi=m, score=s, method=how, n_categories=len(cols),
                            has_total_row=any(path_of[c][-1].casefold() in TOTAL_LABELS for c in cols)))
    dim_mapping = pd.DataFrame(dm_rows)
    mapped_dim = {r["source_value"]: r["matched_klasifikasi"] for r in dm_rows}

    # --- tabel long (unpivot header kolom) ---
    leafs = {c: (path_of[c][-1] if path_of[c] else c) for c in meas_cols}
    grp_of = {c: " > ".join(path_of[c][:-1]) for c in meas_cols}
    distinct_parents = sorted(set(grp_of.values()))
    if len(distinct_parents) == 1 and distinct_parents[0]:
        sub_col, grp_col = slugify(distinct_parents[0].split(" > ")[-1]), None
    else:
        sub_col, grp_col = "kolom", ("kolom_grup" if len(distinct_parents) > 1 else None)
    if sub_col in label_cols:
        sub_col += "_kolom"
    base_cols = label_cols + const_cols + ["_sheet_name", "is_total_row"]
    frames = []
    for order, c in enumerate(meas_cols):
        f = wide_df[base_cols].copy()
        f[sub_col] = leafs[c]
        if grp_col:
            f[grp_col] = grp_of[c]
        f["is_total_col"] = leafs[c].casefold() in TOTAL_LABELS
        f["nilai"] = pd.to_numeric(wide_df[c].astype(float))
        f["_source_row"] = wide_df["_source_row"]
        f["_col_order"] = order
        frames.append(f)
    long_df = pd.concat(frames, ignore_index=True).sort_values(["_source_row", "_col_order"], kind="stable")
    long_df = long_df.drop(columns="_col_order").reset_index(drop=True)
    nilai_type = "bigint" if all(dtypes[c] == "bigint" for c in meas_cols) else "numeric"
    long_df["nilai"] = to_series(long_df["nilai"].where(long_df["nilai"].notna(), None).tolist(), nilai_type)
    long_df["_source_file"] = os.path.basename(opts.file)
    long_df["_loaded_at"] = now
    ordered = (label_cols + const_cols + ["_sheet_name", sub_col] + ([grp_col] if grp_col else []) +
               ["is_total_row", "is_total_col", "nilai", "_source_row", "_source_file", "_loaded_at"])
    long_df = long_df[ordered]
    dtypes_long = {**{c: "text" for c in label_cols + const_cols + ["_sheet_name", sub_col] + ([grp_col] if grp_col else [])},
                   "is_total_row": "boolean", "is_total_col": "boolean", "nilai": nilai_type,
                   "_source_row": "bigint", "_source_file": "text", "_loaded_at": "timestamp"}

    # --- profiling & relasi ---
    prof = rel = None
    if opts.profile:
        extra = {c: {"dash_cells": dash_cells[c]} for c in meas_cols}
        prof = profile_df(g.name, t_wide, wide_df, label_cols + meas_cols + ["is_total_row"], dtypes, extra)
    if opts.relations:
        rel = analyze_relations(g.name, wide_df, label_cols, meas_cols, path_of)
        # kunci kandidat untuk PK
    key_row = rel[rel.relation_type == "candidate_key"] if rel is not None else pd.DataFrame()
    key_cols = ([s.strip() for s in key_row.iloc[0]["left_scope"].split(",")]
                if len(key_row) and key_row.iloc[0]["status"] == "ok" else [])
    pk_wide = (const_cols + key_cols) if key_cols else []
    pk_long = (const_cols + key_cols + [sub_col] + ([grp_col] if grp_col else [])) if key_cols else []

    # --- metadata kolom (langkah 3-5) ---
    colmeta: list[dict] = []

    def cm(table, col, ordinal, role, src, hpath, dtype, desc, defn, match, score, dsrc):
        colmeta.append(dict(sheet_name=g.name, table_name=table, column_name=col, ordinal_position=ordinal,
                            column_role=role, source_col=src, header_path=hpath, inferred_type=dtype,
                            pg_type=PG_NAMES[dtype], description=desc, definition=defn,
                            metadata_match=match, match_score=score, description_source=dsrc))

    n_dim_ok = sum(1 for r in dm_rows if r["source_level"].startswith("baris") and r["matched_klasifikasi"])
    n_dim = sum(1 for r in dm_rows if r["source_level"].startswith("baris"))
    for i, c in enumerate(wide_df.columns, 1):
        d = dtypes[c]
        if c in label_cols:
            k = label_cols.index(c)
            grouped = len(label_cols) > 1 and paths[label_idx[0]] == paths[label_idx[min(k, len(label_idx) - 1)]]
            role = ("dimensi" if k == 0 else "kategori") if len(label_cols) > 1 else "label"
            if k == 0 and len(label_cols) > 1:
                desc = ((f"Nama dimensi/klasifikasi baris. {n_dim_ok}/{n_dim} dimensi berhasil dipetakan ke "
                         f"daftar Klasifikasi di metadata (lihat tabel dim_mapping).") if klas
                        else "Nama dimensi/klasifikasi baris.")
            elif len(label_cols) > 1:
                desc = f"Kategori/nilai dari dimensi pada kolom '{label_cols[0]}'."
            else:
                desc = f"Kolom label baris '{' > '.join(path_of[c])}'."
            cm(t_wide, c, i, role, letter_of[c], " > ".join(path_of[c]), d, desc, None, None, None, "inferred")
        elif c in meas_cols:
            info = indicator_info(meta, path_of[c])
            desc, defn, dsrc = describe_measure(info, path_of[c])
            cm(t_wide, c, i, "ukuran", letter_of[c], " > ".join(path_of[c]), d, desc, defn,
               info.get("nama"), None, dsrc)
        elif c == "is_total_row":
            cm(t_wide, c, i, "flag_turunan", None, None, d,
               "TRUE bila baris adalah subtotal ('Total') suatu dimensi. Jangan dijumlahkan bersama baris lain.",
               None, None, None, "derived")
        elif c in const_cols:
            cm(t_wide, c, i, "konstanta", None, None, d, f"Konstanta dari argumen --const ({c}).",
               None, None, None, "cli")
        else:
            cm(t_wide, c, i, "lineage", None, None, d,
               {"_source_row": "Nomor baris Excel asal (1-based).", "_sheet_name": "Nama sheet Excel asal.",
                "_source_file": "Nama file sumber.",
                "_loaded_at": "Waktu proses load."}[c], None, None, None, "derived")
    info_long = indicator_info(meta, [])
    for i, c in enumerate(long_df.columns, 1):
        d = dtypes_long[c]
        if c in label_cols or c in const_cols:
            src = next(x for x in colmeta if x["table_name"] == t_wide and x["column_name"] == c)
            cm(t_long, c, i, src["column_role"], src["source_col"], src["header_path"], d,
               src["description"], None, None, None, src["description_source"])
        elif c == sub_col:
            pn = distinct_parents[0] if len(distinct_parents) == 1 else None
            m = mapped_dim.get(pn) if pn else None
            cm(t_long, c, i, "dimensi_kolom", None, pn, d,
               f"Nilai header kolom Excel '{pn or 'kolom'}' (hasil unpivot)."
               + (f" Dipetakan ke klasifikasi metadata: {m}." if m else ""), None, m, None, "derived")
        elif c == grp_col:
            cm(t_long, c, i, "dimensi_kolom", None, None, d, "Header induk kolom Excel (hasil unpivot).",
               None, None, None, "derived")
        elif c == "is_total_col":
            cm(t_long, c, i, "flag_turunan", None, None, d,
               "TRUE bila header kolom adalah Total. Hindari double count.", None, None, None, "derived")
        elif c == "is_total_row":
            cm(t_long, c, i, "flag_turunan", None, None, d, "TRUE bila baris adalah subtotal ('Total').",
               None, None, None, "derived")
        elif c == "nilai":
            desc, defn, dsrc = describe_measure(info_long, [])
            cm(t_long, c, i, "ukuran", None, None, d, desc or "Nilai ukuran.", defn, info_long.get("nama"), None, dsrc)
        else:
            src = next(x for x in colmeta if x["table_name"] == t_wide and x["column_name"] == c)
            cm(t_long, c, i, src["column_role"], None, None, d, src["description"], None, None, None, "derived")

    # --- rekomendasi (langkah 9) ---
    nh = L.data_start - L.header_start
    if nh > 1:
        rec("struktur", "info", g.name,
            f"Header {nh} level (baris {L.header_start + 1}-{L.data_start}) digabung jadi satu nama kolom.",
            f"Gunakan tabel {t_long} (unpivot header kolom) untuk analisis/dbt; tabel {t_wide} untuk pengecekan.")
    if n_merge_filled or n_ffill:
        rec("struktur", "info", ", ".join(label_cols[:-1] or label_cols),
            f"{n_merge_filled} sel merge diisi nilai induknya, {n_ffill} sel diisi forward-fill.",
            "Tidak perlu tindakan; jejak baris asli ada di kolom _source_row.")
    n_tr, n_tc = int(wide_df["is_total_row"].sum()), sum(1 for c in meas_cols if leafs[c].casefold() in TOTAL_LABELS)
    if n_tr or n_tc:
        rec("kualitas", "warn", "is_total_row / is_total_col",
            f"Ada {n_tr} baris Total dan {n_tc} kolom Total tercampur dengan data detail.",
            "Selalu filter is_total_row = false (dan is_total_col = false) saat melakukan SUM/AVG agar tidak double count.")
    nd = sum(dash_cells.values())
    if nd:
        zero = "0" if DASH_AS_ZERO else "NULL"
        rec("kualitas", "warn", ", ".join(c for c in meas_cols if dash_cells[c]),
            f"{nd} sel berisi '-' (teks) diubah menjadi {zero}.",
            "Konvensi BPS: '-' = tidak ada/nol. Lihat tabel relation (sum_columns/sum_rows): bila status ok, asumsi 0 terbukti konsisten.")
    if n_ws:
        rec("kualitas", "info", ", ".join(label_cols), f"{n_ws} sel label memiliki spasi berlebih (leading/trailing/ganda) dan dirapikan.",
            "Tidak perlu tindakan.")
    if nonnum:
        rec("kualitas", "warn", ", ".join(meas_cols), f"{len(nonnum)} sel di kolom ukuran bukan angka dan diisi NULL: {'; '.join(nonnum[:5])}",
            "Periksa sel tersebut di Excel sumber.")
    if L.dropped_rows:
        rec("kualitas", "warn", g.name,
            f"{len(L.dropped_rows)} baris di tengah tabel tanpa angka dibuang (baris Excel: {[r + 1 for r in L.dropped_rows][:10]}).",
            "Pastikan baris tersebut memang judul/sub-judul, bukan data.")
    prefixed = {c: int(wide_df[c].dropna().str.match(r"^\s*\d+[.\s]").sum()) for c in label_cols[-1:]}
    for c, k in prefixed.items():
        if k:
            rec("model", "info", c, f"{k} nilai '{c}' diawali nomor/kode (mis. '1. Berusaha sendiri').",
                "Di layer staging dbt pertimbangkan memisah kode & label (hati-hati: '0 Jam (Sementara Tidak Bekerja)' bukan kode).")
    if not klas:
        rec("metadata", "warn", "metadata",
            "Tidak ada sheet/daftar Klasifikasi metadata; arti kolom hanya disimpulkan dari header.",
            "Lengkapi deskripsi kolom secara manual (COMMENT ON COLUMN) atau sediakan sheet 'Standar Data & Metadata'.")
    unmatched = [r["source_value"] for r in dm_rows if not r["matched_klasifikasi"]] if klas else []
    if unmatched:
        rec("metadata", "warn", "dim_mapping", f"Dimensi tanpa padanan di metadata: {unmatched}.",
            "Tambahkan istilah ke SYNONYMS di bagian konfigurasi script.")
    low = [f"{r['source_value']} -> {r['matched_klasifikasi']} ({r['score']})" for r in dm_rows
           if r["matched_klasifikasi"] and r["score"] < 0.85]
    if low:
        rec("metadata", "info", "dim_mapping", f"Pemetaan berskor <0.85 (verifikasi manual): {low}.",
            "Cek tabel dim_mapping dan koreksi bila salah.")
    used = {r["matched_klasifikasi"] for r in dm_rows if r["matched_klasifikasi"]}
    missing = [k for k in klas if k not in used]
    if missing:
        rec("metadata", "info", "klasifikasi", f"Klasifikasi di metadata yang tidak menjadi kolom/dimensi di data: {missing}.",
            "Bila file ini mewakili satu nilai (mis. satu provinsi), simpan sebagai kolom konstanta via --const.")
    texts = " \n".join(str(v) for v in list(meta.dataset["value"].dropna()) +
                       (list(meta.indicator.astype(str).values.ravel()) if meta.indicator is not None else []))
    prov = sorted(set(re.findall(r"[Pp]rovinsi +([A-Z][\w]*(?: +[A-Z][\w]*)*)", texts)))
    per = sorted(set(re.findall(rf"[Pp]eriode +((?:{MONTHS})\b +\d{{4}})", texts)))
    ctx = [f"{k}" for k in ("provinsi", "periode") if k not in const_cols and ((k == "provinsi" and prov) or (k == "periode" and per))]
    if ctx:
        hint = " ".join(([f"--const provinsi='{prov[0]}'"] if "provinsi" in ctx else []) +
                        ([f"--const periode='{per[0]}'"] if "periode" in ctx else []))
        rec("model", "warn", "konteks", f"Tabel data tidak memuat {' & '.join(ctx)}, padahal metadata menyebutkannya.",
            f"Tambahkan kolom konteks agar beberapa file bisa digabung tanpa tertukar: {hint}")
    if pk_long:
        rec("model", "info", t_long, f"Kunci unik terdeteksi: ({', '.join(pk_long)}).",
            "Dipakai sebagai kandidat PRIMARY KEY saat data dimuat ke tabel tujuan.")
    rec("model", "info", t_wide, "Nama dimensi + kategori berulang di setiap baris.",
        "Untuk data warehouse, bentuk dim_karakteristik (karakteristik, kategori, surrogate key) lalu fact(dim_key, kolom_dimensi, nilai).")
    if rel is not None:
        for _, rr in rel[rel.status == "mismatch"].iterrows():
            rec("relasi", "high", f"{rr.left_scope}", f"{rr.relation_type}: {rr.expression} -> {rr.failed or ''} gagal. {rr.detail or ''}",
                "Verifikasi ke publikasi/sumber asli; mungkin ada kategori terpotong, dibulatkan, atau salah ketik.")
        ok = rel[rel.status == "ok"]
        if len(ok):
            rec("relasi", "info", "relation", f"{len(ok)} pemeriksaan relasi lolos ({', '.join(sorted(set(ok.relation_type)))}).",
                "Data konsisten secara internal; aman dipakai.")

    sheet_row = dict(sheet_name=g.name, role="data", n_rows=g.n_rows, n_cols=g.n_cols,
                     n_merged_ranges=len(g.merged), header_first_row=L.header_start + 1,
                     header_last_row=L.data_start, data_first_row=L.data_start + 1, data_last_row=L.data_end + 1,
                     label_columns=", ".join(label_cols), measure_columns=", ".join(meas_cols),
                     notes="; ".join(clean_text(g.values[r][0]) if not is_blank(g.values[r][0]) else
                                     clean_text(next(v for v in g.values[r] if not is_blank(v)))
                                     for r in L.title_rows + L.footer_rows))
    # catatan footer ke meta_dataset
    for r in L.footer_rows + L.title_rows:
        txt = next((clean_text(v) for v in g.values[r] if not is_blank(v)), None)
        if txt:
            kv = kv_from_text(txt)
            meta.dataset.loc[len(meta.dataset)] = [g.name, f"Catatan sheet '{g.name}'", kv[0] if kv else "Catatan",
                                                  kv[1] if kv else txt, f"A{r + 1}", len(meta.dataset) + 1]
    return SheetResult(g.name, t_wide, t_long, wide_df, long_df, dtypes, dtypes_long, colmeta, prof, rel,
                       dim_mapping, recs, sheet_row, pk_wide, pk_long)


# Tipe Postgres hanya dipakai sebagai label metadata (kolom pg_type), bukan untuk load.
