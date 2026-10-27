"""Excel extraction with DuckDB ``read_xlsx``."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List

from ....exceptions import ConfigError
from ...base.extractor import BaseExtractor
from ..utils import parse_fields
from .connection import open_duckdb
from .sql import as_bool, literal


class DuckDBExcelExtractor(BaseExtractor):
    """Yield records from an Excel file read with DuckDB ``read_xlsx``."""

    def reference(self) -> str:
        """The ``read_xlsx`` path: ``s3://``/``minio://``, local, or http(s)."""
        ref = str(self.config.get("url") or "").strip()
        if not ref:
            raise ConfigError("Missing URL for DuckDB Excel extraction")
        if ref.lower().startswith("minio://"):
            from ...storage.minio_storage import split_minio_ref

            bucket, key = split_minio_ref(ref)
            return f"s3://{bucket}/{key}"
        return ref

    def read_xlsx_sql(self, ref: str) -> str:
        options: List[str] = []
        sheet = self.config.get("sheet")
        if sheet:
            options.append(f"sheet={literal(str(sheet))}")
        if self.config.get("header") is not None:
            header = as_bool(self.config.get("header"), True)
            options.append(f"header={'true' if header else 'false'}")
        rng = self.config.get("range")
        if rng:
            options.append(f"range={literal(str(rng))}")
        if as_bool(self.config.get("all_varchar"), True):
            options.append("all_varchar=true")
        suffix = ", " + ", ".join(options) if options else ""
        return f"SELECT * FROM read_xlsx({literal(ref)}{suffix})"

    def apply_columns(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Optional ``columns`` (``Label:name``) rename, mirroring ExcelExtractor."""
        field_map = parse_fields(self.config.get("columns"))
        if not field_map:
            return record
        mapped: Dict[str, Any] = {}
        for field in field_map:
            label = field.get("label") or field.get("source")
            target = field.get("name") or field.get("target") or label
            if label in record:
                mapped[target] = record.get(label)
            elif target in record:
                mapped[target] = record.get(target)
        for key, value in record.items():
            mapped.setdefault(key, value)
        return mapped

    def transform_row(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Hook: adapt a raw row before it leaves the extractor (default: as-is)."""
        return record

    def extract(self) -> Iterator[Dict[str, Any]]:
        ref = self.reference()
        con = open_duckdb(self.config)
        try:
            cursor = con.execute(self.read_xlsx_sql(ref))
            columns = [description[0] for description in cursor.description]
            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                yield self.transform_row(self.apply_columns(record))
        finally:
            con.close()
