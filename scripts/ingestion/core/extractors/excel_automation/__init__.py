"""Excel workbook automation (grids, layouts, metadata, wide/long tables).

The implementation is split by concern; this package keeps the historical
``from ingestion.core.extractors.excel_automation import ...`` API stable.
"""

from __future__ import annotations

from .analysis import analyze_relations, profile_df
from .cli import main, parse_args
from .constants import (
    DASH,
    DASH_AS_ZERO,
    LEVEL_NAMES,
    MATCH_THRESHOLD,
    MAX_IDENT,
    METADATA_SHEET_HINTS,
    MONTHS,
    NOT_NUM,
    NULL_TOKENS,
    OUTPUT_ALIASES,
    OUTPUT_CHOICES,
    OUTPUT_FORMATS,
    PG_NAMES,
    STOPWORDS,
    SYNONYMS,
    TOTAL_LABELS,
)
from .extraction import ExtractionResult, extract_workbook, parse_outputs
from .grid import (
    Grid,
    Layout,
    detect_layout,
    detect_roles,
    header_paths,
    load_grids,
    name_columns,
    slice_grid,
    split_by_markers,
)
from .metadata import (
    Metadata,
    describe_measure,
    indicator_info,
    match_dimension,
    parse_kv_block,
    parse_metadata,
)
from .tables import ExtractionOptions, SheetResult, process_data_sheet
from .utils import (
    clean_text,
    dedupe,
    infer_dtype,
    is_blank,
    is_numlike,
    kv_from_text,
    one_line,
    parse_number,
    shorten_name,
    slugify,
    to_series,
)
from .writers import tables_to_records, to_records, write_csvs, write_tables

__all__ = [
    "DASH", "DASH_AS_ZERO", "ExtractionOptions", "ExtractionResult", "Grid",
    "LEVEL_NAMES", "Layout", "MATCH_THRESHOLD", "MAX_IDENT",
    "METADATA_SHEET_HINTS", "MONTHS", "Metadata", "NOT_NUM", "NULL_TOKENS",
    "OUTPUT_ALIASES", "OUTPUT_CHOICES", "OUTPUT_FORMATS", "PG_NAMES",
    "STOPWORDS", "SYNONYMS", "SheetResult", "TOTAL_LABELS",
    "analyze_relations", "clean_text", "dedupe", "describe_measure",
    "detect_layout", "detect_roles", "extract_workbook", "header_paths",
    "indicator_info", "infer_dtype", "is_blank", "is_numlike", "kv_from_text",
    "load_grids", "main", "match_dimension", "name_columns", "one_line",
    "parse_args",
    "parse_kv_block", "parse_metadata", "parse_number", "parse_outputs",
    "process_data_sheet", "profile_df", "shorten_name", "slice_grid",
    "slugify", "split_by_markers", "tables_to_records", "to_records",
    "to_series", "write_csvs", "write_tables",
]
