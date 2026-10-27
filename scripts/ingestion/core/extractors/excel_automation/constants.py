"""Excel workbook automation — constants."""

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

# =============================================================================
# KONFIGURASI (ubah di sini bila format file berbeda)
# =============================================================================
MAX_IDENT = 55                      # batas panjang nama kolom (Postgres max 63 byte)
DASH_AS_ZERO = True                 # sel '-' dianggap 0 (konvensi BPS). False -> NULL
TOTAL_LABELS = {"total", "jumlah", "jumlah total", "grand total"}
METADATA_SHEET_HINTS = ("metadata", "standar data", "kamus", "dictionary")
NULL_TOKENS = {"n/a", "na", "nan", "null", "none", "..", "..."}
LEVEL_NAMES = ["", "kategori", "subkategori"]      # nama kolom label bertingkat
MATCH_THRESHOLD = 0.6               # ambang kemiripan nama dimensi <-> metadata
STOPWORDS = {
    "yang", "di", "dan", "atau", "seluruh", "kategori", "klasifikasi", "jumlah",
    "seminggu", "lalu", "tahun", "dari", "pada", "untuk", "dengan", "ke", "menurut",
}
# Singkatan/istilah yang tidak mirip secara teks dengan nama klasifikasi di metadata.
# Tambahkan sesuai domain data Anda.
SYNONYMS = {
    "kbji": "jabatan",
    "kbli": "lapangan usaha",
    "perkotaan": "daerah tempat tinggal",
    "perdesaan": "daerah tempat tinggal",
    "pedesaan": "daerah tempat tinggal",
}
MONTHS = ("Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|"
          "Nopember|November|Desember")

# =============================================================================
# UTILITAS DASAR
# =============================================================================
RE_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
RE_ISO_TS = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")
_RE_ID = re.compile(r"^[-+]?\d{1,3}(\.\d{3})+(,\d+)?$")     # 1.234.567,89
_RE_EN = re.compile(r"^[-+]?\d{1,3}(,\d{3})+(\.\d+)?$")     # 1,234,567.89
_RE_PLAIN = re.compile(r"^[-+]?\d+([.,]\d+)?$")             # 12 / 12,5 / 12.5
KV_RE = re.compile(r"^\s*([^:\n]{1,40}?)\s*:\s*(\S.*)$", re.S)


class _Sentinel:
    def __init__(self, n): self.n = n
    def __repr__(self): return self.n


DASH = _Sentinel("DASH")          # sel berisi '-' / ' -   '
NOT_NUM = _Sentinel("NOT_NUM")    # string yang bukan angka

# Tipe Postgres hanya dipakai sebagai label metadata (kolom pg_type), bukan untuk load.
PG_NAMES = {"bigint": "BIGINT", "numeric": "NUMERIC", "boolean": "BOOLEAN", "date": "DATE",
            "timestamp": "TIMESTAMP", "text": "TEXT"}

# =============================================================================
# OUTPUT PILIHAN
# =============================================================================
OUTPUT_CHOICES = ["data", "data_long", "dim_mapping", "meta_sheet", "meta_dataset", "meta_indicator",
                  "meta_column", "profile", "relation", "recommendation"]
OUTPUT_ALIASES = {"relations": "relation", "long": "data_long", "wide": "data", "rekomendasi": "recommendation"}

OUTPUT_FORMATS = ["csv", "json", "ndjson"]
