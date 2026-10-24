

"""Dictionary driven schema mapping (TDD section 8).

The dictionary tells the extractor *which* fields the caller wants and under
which names (aliases) they may appear in the document.  Nothing is invented:
a field that cannot be matched to a column, a row label, a group header or
the page context is reported as unmapped.

Supported dictionary sources
----------------------------
* a :class:`~pdf_extractor.models.Dictionary` instance,
* a ``dict`` (the JSON contract),
* a JSON file,
* a Pydantic model class,
* a ``.py`` file that defines one or more Pydantic models.
"""
from __future__ import annotations

import importlib.util
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from pydantic import BaseModel

from .models import Dictionary, DictionaryOptions, FieldSpec, Provenance
from .page_context import PageContext, coerce, unit_from_header
from .pdf_reader import normalise
from .table_extractor import TableBlock, TableStructure, split_bilingual

log = logging.getLogger("pdf_extractor.mapper")

_YEAR_WORD = re.compile(r"(?i)\b(tahun|year|periode|period)\b")
_GROUP_WORD = re.compile(
    r"(?i)(kelompok|group|grup|kategori|category|jenis|type|tipe|sektor|sector|klasifikasi)"
)
_UNIT_WORD = re.compile(r"(?i)(satuan|unit|uom)")
_YEAR_VALUE = re.compile(r"^(19|20)\d{2}$")

#: words that turn a long unit label into its short form
_UNIT_CANONICAL = {
    "gigajoule": "GJ", "giga joule": "GJ", "joule": "J", "terajoule": "TJ",
    "kiloliter": "kL", "kilogram": "kg", "ton": "ton", "barel": "barel",
    "million boe": "Million BOE", "boe": "BOE", "toe": "TOE",
    "kilowatt hour": "kWh", "megawatt hour": "MWh", "gigawatt hour": "GWh",
}


# --------------------------------------------------------------------------
# dictionary loading
# --------------------------------------------------------------------------
def load_dictionary(source: Any, model_class: str | None = None) -> Dictionary:
    """Build a :class:`Dictionary` from any supported source."""
    if isinstance(source, Dictionary):
        return source
    if isinstance(source, dict):
        return _from_dict(source)
    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.suffix.lower() == ".json":
            return _from_dict(json.loads(path.read_text(encoding="utf-8")))
        if path.suffix.lower() == ".py":
            return _from_python(path, model_class)
        raise ValueError(f"format dictionary tidak didukung: {path}")
    if isinstance(source, type) and issubclass(source, BaseModel):
        return _from_model(source)
    raise TypeError(f"sumber dictionary tidak dikenali: {type(source)!r}")


def _from_dict(data: dict) -> Dictionary:
    fields: list[FieldSpec] = []
    raw_fields = data.get("fields")
    if isinstance(raw_fields, dict):
        for name, spec in raw_fields.items():
            spec = dict(spec or {})
            spec.setdefault("name", name)
            fields.append(FieldSpec(**spec))
    elif isinstance(raw_fields, list):
        for spec in raw_fields:
            fields.append(FieldSpec(**spec))
    options = DictionaryOptions(**(data.get("options") or {}))
    return Dictionary(name=data.get("model") or data.get("name") or "Record",
                      fields=fields, options=options)


def _from_model(model: type[BaseModel]) -> Dictionary:
    fields: list[FieldSpec] = []
    for name, f in model.model_fields.items():
        aliases: list[str] = []
        extra = getattr(f, "json_schema_extra", None) or {}
        if isinstance(extra, dict):
            aliases = list(extra.get("aliases") or [])
        if f.alias:
            aliases.append(f.alias)
        annotation = str(f.annotation)
        ftype = "str"
        for key in ("int", "float", "bool", "date"):
            if key in annotation.lower():
                ftype = key
                break
        derived = extra.get("derived") if isinstance(extra, dict) else None
        fields.append(
            FieldSpec(name=name, type=ftype, aliases=aliases,
                      required=bool(getattr(f, "is_required", lambda: False)()),
                      derived=derived)
        )
    return Dictionary(name=model.__name__, fields=fields)


def _from_python(path: Path, model_class: str | None) -> Dictionary:
    """Import ``path`` and pick a Pydantic model from it."""
    module_name = f"pdf_extractor_dict_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"tidak bisa mengimpor {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    candidates = [
        obj for obj in vars(module).values()
        if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel
    ]
    if not candidates:
        # a plain module level dict / Dictionary object is fine too
        for obj in vars(module).values():
            if isinstance(obj, Dictionary):
                return obj
            if isinstance(obj, dict) and "fields" in obj:
                return _from_dict(obj)
        raise ValueError(f"tidak ada model Pydantic di {path}")
    if model_class:
        for obj in candidates:
            if obj.__name__ == model_class:
                return _from_model(obj)
        raise ValueError(f"class {model_class!r} tidak ditemukan di {path}")
    for obj in candidates:
        if obj.__name__ in ("Record", "Row", "Data"):
            return _from_model(obj)
    return _from_model(candidates[-1])


# --------------------------------------------------------------------------
# column mapping
# --------------------------------------------------------------------------
def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9%]+", normalise(text).lower()) if t]


def _score(cell: str, names: Sequence[str]) -> float:
    """Similarity between a header cell and one of the wanted names (0..1)."""
    if not cell or not names:
        return 0.0
    ct = set(_tokens(cell))
    low = normalise(cell).lower()
    best = 0.0
    for name in names:
        nt = _tokens(name)
        if not nt:
            continue
        overlap = len(set(nt) & ct) / len(set(nt) | set(nt))
        contained = 1.0 if normalise(name).lower() in low else 0.0
        best = max(best, overlap, contained)
    return best


@dataclass
class ColumnMapping:
    field: str
    column: int | None = None
    header: str | None = None
    source: str = "column_header"
    score: float = 0.0


def map_columns(
    header: Sequence[str],
    dictionary: Dictionary,
    threshold: float = 0.5,
) -> dict[str, ColumnMapping]:
    """Match dictionary fields to table columns."""
    mapping: dict[str, ColumnMapping] = {}
    used: set[int] = set()
    specs = [f for f in dictionary.fields if not f.derived]
    # strongest match first so a specific alias wins over a generic one
    pairs: list[tuple[float, FieldSpec, int]] = []
    for spec in specs:
        for col, cell in enumerate(header):
            sc = _score(cell, spec.candidates())
            if sc >= threshold:
                pairs.append((sc, spec, col))
    for sc, spec, col in sorted(pairs, key=lambda p: -p[0]):
        if spec.name in mapping or col in used:
            continue
        mapping[spec.name] = ColumnMapping(
            field=spec.name, column=col, header=normalise(header[col]),
            source="column_header", score=sc,
        )
        used.add(col)
    return mapping


def canonical_unit(values: Sequence[str]) -> str | None:
    """``['GigaJoule', '(GJ)']`` -> ``'GJ'``."""
    joined = " ".join(v for v in values if v)
    if not joined:
        return None
    short = unit_from_header(joined)
    if short:
        short = short.strip("() ")
        if short and not re.fullmatch(r"(?i)gigajoule", short):
            return short
    for word in _UNIT_CANONICAL:
        if re.search(rf"(?i)\b{re.escape(word)}\b", joined):
            return _UNIT_CANONICAL[word]
    return normalise(joined.split("|")[0])[:24] or None


# --------------------------------------------------------------------------
# table -> records
# --------------------------------------------------------------------------
@dataclass
class MappedTable:
    records: list[dict[str, Any]] = field(default_factory=list)
    provenance: list[Provenance] = field(default_factory=list)
    mapping: dict[str, ColumnMapping] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    unmapped: list[str] = field(default_factory=list)


_NUM_CELL = re.compile(r"^-?[\d.,()%\s]+$")
_LABEL_NOISE = re.compile(r"^\s*(?:[-–—•]|\d+|\(?[a-z]\)|[a-z]\.)\s*")
#: a word split across a line break: "Renew-" + "ables", "Geo-" + "thermal".
#: Only a *lower case* continuation is joined, so "Non- PLN" stays as it is.
_HYPHEN_WRAP = re.compile(r"(?<=[A-Za-z])[-‐-―]\s+(?=[a-z])")


def dehyphenate(text: str) -> str:
    """Rejoin a word that the PDF broke across a line break."""
    return _HYPHEN_WRAP.sub("", normalise(text))


def _field_match(label: str, field: FieldSpec) -> tuple[float, int]:
    """``(score, length of the alias that produced it)`` for one field.

    The length breaks ties towards the more specific alias: a row
    "IPP, Captive Power, and PPU (Non-PLN)" contains both "PLN" and
    "and PPU (Non-PLN)", and the longer one is the intended match.
    """
    best_score, best_len = 0.0, 0
    for name in field.candidates():
        s = _score(label, [name])
        n = len(normalise(name))
        if s > best_score or (s == best_score and s > 0 and n > best_len):
            best_score, best_len = s, n
    return best_score, best_len


def _label_column(rows: Sequence[Sequence[str]], dictionary: Dictionary) -> tuple[int, float]:
    """Index of the column that holds the row labels, and how well it fits."""
    fields = [f for f in dictionary.fields if not f.derived]
    ncols = max((len(r) for r in rows), default=0)
    best_col, best_score = 0, 0.0
    for c in range(ncols):
        raw = [normalise(r[c]) for r in rows if c < len(r)]
        raw = [v for v in raw if v]
        cells = [v for v in raw if not _NUM_CELL.match(v)]
        # a column of values is never the label column, even if one of its
        # cells happens to carry a name (stacked headers do)
        if not cells or len(cells) < 0.6 * len(raw):
            continue
        score = sum(
            max((_score(_LABEL_NOISE.sub("", v), f.candidates()) for f in fields), default=0.0)
            for v in cells
        ) / len(cells)
        if score > best_score:
            best_col, best_score = c, score
    return best_col, best_score


def map_table(
    block: TableBlock,
    structure: TableStructure,
    dictionary: Dictionary,
    context: PageContext | None = None,
    file_name: str | None = None,
    marker: str | None = None,
) -> MappedTable:
    """Turn one table block into dictionary conform records."""
    non_derived = [f for f in dictionary.fields if not f.derived]
    if dictionary.options.allow_transposed and non_derived and len(block.rows) >= 3:
        # a matrix table names the wanted fields down its first column and
        # keeps one *record* per remaining column (energy balance tables)
        label_col, label_score = _label_column(block.rows, dictionary)
        header_score = (len(map_columns(structure.header, dictionary)) / len(non_derived)
                        if non_derived else 0.0)
        if label_score > header_score + 0.1:
            return map_transposed(block, structure, dictionary, label_col,
                                  context, file_name, marker)

    out = MappedTable()
    mapping = map_columns(structure.header, dictionary)
    out.mapping = mapping
    specs = {f.name: f for f in dictionary.fields}

    # -- fields that are not a column -------------------------------------
    group_field = next(
        (f.name for f in dictionary.fields
         if not f.derived and f.name not in mapping and _GROUP_WORD.search(f.name)
         or any(_GROUP_WORD.search(a) for a in f.aliases)),
        None,
    )
    if group_field is None:
        group_field = next(
            (f.name for f in dictionary.fields
             if not f.derived and f.name not in mapping
             and f.kind == "str" and not _UNIT_WORD.search(f.name)
             and structure.groups),
            None,
        )
    year_field = next(
        (f.name for f in dictionary.fields
         if not f.derived and f.name not in mapping
         and (f.kind == "int") and _YEAR_WORD.search(f.name)),
        None,
    )
    unit_field = next(
        (f.name for f in dictionary.fields
         if not f.derived and f.name not in mapping and f.kind == "str"
         and (_UNIT_WORD.search(f.name) or any(_UNIT_WORD.search(a) for a in f.aliases))),
        None,
    )
    # a unit column ("Satuan Unit") is normalised to its short form (GJ)
    unit_columns: dict[int, str] = {}
    for i, h in enumerate(structure.header):
        if not _UNIT_WORD.search(h):
            continue
        value = canonical_unit([r[i] for r in block.rows if i < len(r)])
        if value:
            unit_columns[i] = value
        elif unit_field is not None and unit_field not in mapping:
            mapping[unit_field] = ColumnMapping(unit_field, i, normalise(h),
                                                "column_header", 1.0)

    context_values: dict[str, tuple[Any, str]] = {}
    for name, spec in specs.items():
        if name in mapping or spec.derived or context is None:
            continue
        found = context.find(spec)
        if found is not None:
            context_values[name] = found

    # a group field is filled from the group headers, not from a column, so it
    # is only "unmapped" when the table actually has no groups
    group_resolved = group_field if (group_field and structure.groups) else None
    for name in specs:
        if name in mapping or name in context_values or specs[name].derived:
            continue
        if name == group_resolved:
            continue
        out.unmapped.append(name)
    if out.unmapped:
        out.warnings.append(
            "field tidak terpetakan ke kolom: " + ", ".join(out.unmapped)
        )

    # -- rows ---------------------------------------------------------------
    keep_totals = dictionary.options.keep_totals
    total_pattern = re.compile(dictionary.options.total_pattern)
    for row_index in structure.data_rows:
        cells = block.rows[row_index]
        if row_index in structure.total_rows and not keep_totals:
            continue
        record: dict[str, Any] = {}
        sources: dict[str, str] = {}

        def put(name: str, value: Any, source: str) -> None:
            if value is None or (isinstance(value, str) and not value.strip()):
                return
            if isinstance(value, str) and specs.get(name) and specs[name].kind == "str":
                # "Bahan Bakar Minyak | Fuel Oil" -> keep the label the report
                # prints first; the raw cell stays visible in the provenance
                value = split_bilingual(value)
            record[name] = coerce(value, specs[name].kind) if name in specs else value
            sources[name] = source

        for name, mp in mapping.items():
            if mp.column is None or mp.column >= len(cells):
                continue
            if mp.column in unit_columns:
                put(name, unit_columns[mp.column], "column_header")
                continue
            raw = normalise(cells[mp.column])
            put(name, raw, "table_cell")
        if group_field is not None:
            grp = structure.groups.get(row_index)
            if grp:
                put(group_field, grp, "group_header")
        if year_field is not None and year_field in context_values:
            put(year_field, context_values[year_field][0], context_values[year_field][1])
        for name, (value, source) in context_values.items():
            if name not in record and name != year_field:
                put(name, value, source)
        if not record:
            continue

        label = split_bilingual(normalise(next((c for c in cells if c), "")))
        is_total = row_index in structure.total_rows or bool(total_pattern.match(label))
        record["_is_total"] = is_total  # internal, removed below
        record["_label"] = label
        out.records.append(record)
        out.provenance.append(
            Provenance(
                file_name=file_name,
                page=block.page,
                marker=marker,
                kind="table",
                source_headers=[normalise(h) for h in structure.header],
                row_index=row_index,
                value_sources=sources,
            )
        )
    return out


# --------------------------------------------------------------------------
# transposed (matrix) table -> records
# --------------------------------------------------------------------------
def map_transposed(
    block: TableBlock,
    structure: TableStructure,
    dictionary: Dictionary,
    label_col: int,
    context: PageContext | None = None,
    file_name: str | None = None,
    marker: str | None = None,
) -> MappedTable:
    """One record per *column*; the dictionary fields name the row labels.

    Energy balance tables are printed this way: the flow stages
    (``Primary Energy Supply``, ``Production`` ...) run down the first column
    while every energy type owns a column of its own.
    """
    out = MappedTable()
    specs = {f.name: f for f in dictionary.fields}
    fields = [f for f in dictionary.fields if not f.derived]
    rows = block.rows
    ncols = max((len(r) for r in rows), default=0)
    row_indexes = structure.data_rows or list(range(len(rows)))

    # the value columns are the numeric ones; the others carry labels/units
    value_cols: list[int] = []
    for c in range(ncols):
        if c == label_col:
            continue
        vals = [normalise(r[c]) for r in rows if c < len(r)]
        vals = [v for v in vals if v]
        if not vals:
            continue
        numeric = sum(1 for v in vals if _NUM_CELL.match(v))
        if numeric / len(vals) >= 0.6:
            value_cols.append(c)
    if not value_cols:
        return out

    def column_name(c: int) -> str:
        head = normalise(structure.header[c]) if c < len(structure.header) else ""
        if head and not _NUM_CELL.match(head):
            return split_bilingual(dehyphenate(head))
        for r in rows:
            v = normalise(r[c]) if c < len(r) else ""
            if v and not _NUM_CELL.match(v):
                return split_bilingual(dehyphenate(v))
        return ""

    name_field = next(
        (f.name for f in fields
         if f.kind == "str" and not _UNIT_WORD.search(f.name)
         and not any(_UNIT_WORD.search(a) for a in f.aliases)
         and not _YEAR_WORD.search(f.name)),
        None,
    )
    year_field = next(
        (f.name for f in fields if f.kind == "int" and _YEAR_WORD.search(f.name)), None
    )
    unit_field = next(
        (f.name for f in fields if f.kind == "str"
         and (_UNIT_WORD.search(f.name) or any(_UNIT_WORD.search(a) for a in f.aliases))),
        None,
    )
    total_pattern = re.compile(dictionary.options.total_pattern)
    keep_totals = dictionary.options.keep_totals

    # row label -> dictionary field.  Rows *compete* for the fields: the best
    # scoring row claims a field and nobody else may take it again, otherwise
    # two rows would fight over "State Own Utility (PLN)" and the later one
    # would silently overwrite the correct value.
    skip = {name_field, year_field, unit_field}
    claims: list[tuple[float, int, int, list[tuple[str, float]]]] = []
    for i in row_indexes:
        if label_col >= len(rows[i]):
            continue
        label = _LABEL_NOISE.sub("", dehyphenate(normalise(rows[i][label_col])))
        if not label:
            continue
        ranked = sorted(
            ((name, *_field_match(label, f))
             for f in fields if f.name not in skip and (name := f.name)),
            key=lambda t: (-t[1], -t[2]),
        )
        if not ranked or ranked[0][1] < 0.6:
            continue
        claims.append((ranked[0][1], ranked[0][2], i, [(n, s) for n, s, _ in ranked]))
    claims.sort(key=lambda c: (-c[0], -c[1], c[2]))

    label_to_field: dict[int, tuple[str, float]] = {}
    taken: set[str] = set()
    for top_score, _top_len, i, ranked in claims:
        for name, score in ranked:
            if name in taken or score < 0.6 or score < top_score * 0.8:
                continue
            label_to_field[i] = (name, score)
            taken.add(name)
            break

    unit_value = None
    if unit_field is not None and context is not None:
        found = context.find(specs[unit_field])
        if found is not None:
            unit_value = found[0]
    if unit_value is None:
        unit_value = unit_from_header(" ".join(column_name(c) for c in value_cols))
    if unit_value is None:
        unit_value = unit_from_header(" ".join(normalise(h) for h in structure.header))

    year_value = None
    if year_field is not None and context is not None and context.years:
        year_value = max(context.years)

    for c in value_cols:
        label = column_name(c)
        if not label:
            continue
        is_total = bool(total_pattern.match(label)) or label.lower() == "total"
        if is_total and not keep_totals:
            continue
        record: dict[str, Any] = {}
        sources: dict[str, str] = {}
        if name_field:
            record[name_field] = label
            sources[name_field] = "column_header"
        for i, (fname, _s) in label_to_field.items():
            raw = normalise(rows[i][c]) if c < len(rows[i]) else ""
            if not raw or not _NUM_CELL.match(raw):
                continue
            try:
                record[fname] = coerce(raw, specs[fname].kind)
                sources[fname] = "table_cell"
            except ValueError:
                continue
        if year_field and year_value is not None:
            record[year_field] = year_value
            sources[year_field] = "page_context"
        if unit_field and unit_value:
            record[unit_field] = unit_value
            sources[unit_field] = "page_context"
        if len(record) <= 1:
            continue
        record["_is_total"] = is_total
        record["_label"] = label
        out.records.append(record)
        out.provenance.append(
            Provenance(
                file_name=file_name,
                page=block.page,
                marker=marker,
                kind="table",
                method="deterministic",
                source_headers=[normalise(h) for h in structure.header],
                row_index=c,
                value_sources=sources,
            )
        )
    # report the fields the matrix could not fill
    filled = {n for r in out.records for n in r if not n.startswith("_")}
    out.unmapped = [f.name for f in fields if f.name not in filled]
    if out.unmapped:
        out.warnings.append("field tidak terpetakan ke baris: " + ", ".join(out.unmapped))
    out.mapping = {
        fname: ColumnMapping(fname, label_col, "transposed", "row_label", score)
        for fname, score in label_to_field.values()
    }
    return out


# --------------------------------------------------------------------------
# chart -> records
# --------------------------------------------------------------------------
def _pick_category(chart, context: PageContext | None) -> str | None:
    """Which category (usually a year) is the one the user asked for?"""
    categories = chart.categories
    if not categories:
        return None
    years = [c for c in categories if _YEAR_VALUE.match(normalise(c))]
    wanted: list[int] = []
    if context is not None and years:
        wanted = [y for y in context.years if str(y) in {normalise(c) for c in years}]
    if chart.title_years:
        wanted = [y for y in chart.title_years if str(y) in {normalise(c) for c in years}]
    if years:
        if wanted:
            return str(max(wanted))
        return normalise(years[-1])
    return normalise(categories[-1])


def map_chart(
    chart,
    dictionary: Dictionary,
    context: PageContext | None = None,
    file_name: str | None = None,
    marker: str | None = None,
) -> MappedTable:
    """Turn :class:`~pdf_extractor.chart_extractor.ChartData` into records."""
    out = MappedTable()
    specs = {f.name: f for f in dictionary.fields}
    category = _pick_category(chart, context)
    series_names = chart.series or []
    values = chart.values  # {(series, category): value}

    # -- classify the dictionary fields -----------------------------------
    value_field = next(
        (f.name for f in dictionary.fields
         if not f.derived and f.kind in ("int", "float")
         and not _YEAR_WORD.search(f.name)
         and not any(_YEAR_WORD.search(a) for a in f.aliases)),
        None,
    )
    year_field = next(
        (f.name for f in dictionary.fields
         if not f.derived and f.kind == "int" and _YEAR_WORD.search(f.name)),
        None,
    )
    series_field = next(
        (f.name for f in dictionary.fields
         if not f.derived and f.kind == "str" and f.name != year_field
         and not _UNIT_WORD.search(f.name)),
        None,
    )
    out.mapping = {
        (value_field or ""): ColumnMapping(value_field or "", None, chart.title,
                                           "chart_data_label", 1.0)
    }

    prev_category = None
    if category is not None and len(chart.categories) > 1:
        idx = chart.categories.index(category) if category in chart.categories else -1
        if idx > 0:
            prev_category = chart.categories[idx - 1]

    total = chart.total
    total_prev = None
    if total is not None and prev_category is not None:
        parts = [values.get((s, prev_category)) for s in series_names]
        parts = [p for p in parts if p is not None]
        if parts:
            total_prev = sum(parts)

    def build(name: str | None, value: float | None, share: float | None,
              yoy: float | None, is_total: bool) -> dict[str, Any]:
        rec: dict[str, Any] = {}
        if series_field and name is not None:
            rec[series_field] = name
        if value_field and value is not None:
            rec[value_field] = coerce(value, specs[value_field].kind)
        if year_field and category is not None:
            try:
                rec[year_field] = int(normalise(category))
            except ValueError:
                pass
        elif year_field and context is not None:
            years = context.years
            if years:
                rec[year_field] = max(years)
        for f in dictionary.derived_fields:
            if f.derived == "share_of_total":
                rec[f.name] = None if share is None else round(share, 1)
            elif f.derived == "yoy":
                rec[f.name] = None if yoy is None else round(yoy, 1)
        rec["_is_total"] = is_total
        return rec

    for s in series_names:
        value = values.get((s, category))
        if value is None:
            continue
        prev = values.get((s, prev_category)) if prev_category else None
        share = chart.shares.get(s)
        if share is None and total:
            share = value / total * 100.0
        yoy = None
        if prev not in (None, 0):
            yoy = (value / prev - 1.0) * 100.0
        rec = build(s, value, share, yoy, False)
        rec["_label"] = s
        out.records.append(rec)
        out.provenance.append(
            Provenance(file_name=file_name, page=chart.page, marker=marker,
                       kind="chart", method="deterministic",
                       source_headers=series_names,
                       value_sources={
                           (value_field or "value"): "chart_data_label",
                           **{f.name: "derived" for f in dictionary.derived_fields},
                       })
        )

    if total is not None and series_field:
        share = 100.0
        yoy = None
        if total_prev not in (None, 0):
            yoy = (total / total_prev - 1.0) * 100.0
        rec = build(dictionary.options.total_label, total, share, yoy, True)
        rec["_label"] = dictionary.options.total_label
        out.records.append(rec)
        out.provenance.append(
            Provenance(file_name=file_name, page=chart.page, marker=marker,
                       kind="chart", method="deterministic",
                       source_headers=series_names,
                       value_sources={(value_field or "value"): chart.total_source or "derived"},
                       confidence=0.9 if chart.total_source == "chart_data_label" else 0.8)
        )
    return out