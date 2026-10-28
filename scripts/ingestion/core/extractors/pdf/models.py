
"""Core data models for :mod:`pdf_extractor`.

The models here define the *contract* between the package and its callers:

* :class:`FieldSpec` / :class:`Dictionary` -- the user supplied output schema.
* :class:`Provenance` -- traceability of a single record (page, method, ...).
* :class:`ExtractionResult` -- the object returned by :func:`extract_pdf`.

Business records themselves are plain ``dict`` objects so that they never
violate the user defined schema; provenance travels separately.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# --------------------------------------------------------------------------
# Types
# --------------------------------------------------------------------------
FIELD_TYPES: dict[str, type] = {
    "str": str,
    "string": str,
    "text": str,
    "int": int,
    "integer": int,
    "float": float,
    "number": float,
    "decimal": float,
    "bool": bool,
    "boolean": bool,
    "date": str,
    "datetime": str,
}

#: How a value was obtained.  Used for provenance and for LLM guardrails.
VALUE_SOURCES = (
    "table_cell",
    "column_header",
    "row_label",
    "group_header",
    "page_title",
    "nearby_text",
    "chart_data_label",
    "chart_calibrated",
    "derived",
    "llm_inferred",
)


class Status(str, Enum):
    """Terminal status of an extraction run (see TDD section 14)."""

    SUCCESS = "success"
    PARTIAL = "partial"
    INVALID_PDF = "invalid_pdf"
    INVALID_PAGE_RANGE = "invalid_page_range"
    INSUFFICIENT_TEXT_LAYER = "insufficient_text_layer"
    MARKER_NOT_FOUND = "marker_not_found"
    DATA_CANDIDATE_NOT_FOUND = "data_candidate_not_found"
    AMBIGUOUS_CANDIDATE = "ambiguous_candidate"
    SCHEMA_MAPPING_FAILED = "schema_mapping_failed"
    VALIDATION_FAILED = "validation_failed"
    LLM_REQUEST_FAILED = "llm_request_failed"

    @property
    def is_ok(self) -> bool:
        return self in (Status.SUCCESS, Status.PARTIAL)


class ExtractionMethod(str, Enum):
    DETERMINISTIC = "deterministic"
    LLM = "llm"


class ExtractionKind(str, Enum):
    TABLE = "table"
    CHART = "chart"


# --------------------------------------------------------------------------
# Dictionary / schema
# --------------------------------------------------------------------------
class FieldSpec(BaseModel):
    """A single output field.

    ``derived`` allows fields that are not printed in the document but can be
    computed from extracted values:

    * ``share_of_total`` -- value / total * 100 (percent share)
    * ``yoy``            -- (value[t] / value[t-1] - 1) * 100 (growth percent)
    """

    model_config = ConfigDict(extra="ignore")

    name: str
    type: str = "str"
    aliases: list[str] = Field(default_factory=list)
    description: str = ""
    required: bool = False
    derived: str | None = None
    derived_of: str | None = None
    unit: str | None = None

    @property
    def kind(self) -> str:
        """Normalised python type name (``str``/``int``/``float``/``bool``)."""
        t = (self.type or "str").lower()
        if t in FIELD_TYPES:
            py = FIELD_TYPES[t]
            return {str: "str", int: "int", float: "float", bool: "bool"}.get(py, "str")
        return "str"

    def candidates(self) -> list[str]:
        """All header names that may identify this field."""
        seen: list[str] = []
        for cand in [self.name, *self.aliases]:
            cand = (cand or "").strip()
            if cand and cand.lower() not in {s.lower() for s in seen}:
                seen.append(cand)
        return seen


class DictionaryOptions(BaseModel):
    """Table/chart level options carried by the dictionary."""

    model_config = ConfigDict(extra="ignore")

    keep_totals: bool = True
    #: add an aggregated ``Total`` row when the source has no explicit one
    add_total_row: bool = False
    total_label: str = "Total"
    total_pattern: str = r"(?i)^(grand\s+)?(total|jumlah|subtotal)\b"
    #: fields may also be filled from the first column (transposed tables)
    allow_transposed: bool = True


class Dictionary(BaseModel):
    """User defined output schema."""

    model_config = ConfigDict(extra="ignore")

    name: str = "Record"
    fields: list[FieldSpec] = Field(default_factory=list)
    options: DictionaryOptions = Field(default_factory=DictionaryOptions)

    def field(self, name: str) -> FieldSpec | None:
        return next((f for f in self.fields if f.name == name), None)

    @property
    def derived_fields(self) -> list[FieldSpec]:
        return [f for f in self.fields if f.derived]


# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------
class Provenance(BaseModel):
    """Traceability information for one record."""

    model_config = ConfigDict(extra="ignore")

    file_name: str | None = None
    page: int | None = None
    pages: list[int] = Field(default_factory=list)
    marker: str | None = None
    kind: ExtractionKind | str | None = None
    method: ExtractionMethod | str = ExtractionMethod.DETERMINISTIC
    source_headers: list[str] = Field(default_factory=list)
    row_index: int | None = None
    confidence: float = 1.0
    value_sources: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class SourceInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    file_name: str
    file_path: str | None = None
    pages: list[int] = Field(default_factory=list)
    page_count: int | None = None


class ExtractionResult(BaseModel):
    """Result of :func:`pdf_extractor.extract_pdf`.

    ``records`` only contains business fields (schema conformant); everything
    else lives in ``provenance`` / ``metadata`` / ``warnings`` / ``errors``.
    """

    model_config = ConfigDict(extra="ignore")

    status: Status = Status.SUCCESS
    marker: str | None = None
    source: SourceInfo
    records: list[dict[str, Any]] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # -- convenience ------------------------------------------------------
    @property
    def ok(self) -> bool:
        return self.status.is_ok and not self.errors

    def items(self) -> list[tuple[dict[str, Any], Provenance]]:
        """Records paired with their provenance (best effort alignment)."""
        out: list[tuple[dict[str, Any], Provenance]] = []
        for i, rec in enumerate(self.records):
            prov = self.provenance[i] if i < len(self.provenance) else Provenance()
            out.append((rec, prov))
        return out

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def to_json(self, path: str | Path, indent: int = 2) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.model_dump_json(indent=indent, exclude_none=False), encoding="utf-8")
        return p

    def to_ndjson(self, path: str | Path) -> Path:
        import json

        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            for rec in self.records:
                fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        return p

    def to_csv(self, path: str | Path) -> Path:
        import csv

        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        cols: list[str] = []
        for rec in self.records:
            for k in rec:
                if k not in cols:
                    cols.append(k)
        with p.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for rec in self.records:
                w.writerow(rec)
        return p