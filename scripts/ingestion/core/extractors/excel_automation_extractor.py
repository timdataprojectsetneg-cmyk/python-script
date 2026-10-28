"""Ingestion adapter for the Excel workbook automation engine.

`ExcelExtractor` downloads a workbook and yields its raw rows. This adapter is
for workbooks whose sheets need the automation engine (multi-level headers,
metadata sheet, wide/long tables). It reads the workbook, runs
:func:`~ingestion.core.extractors.excel_automation.extract_workbook`, selects one
output table, and yields its records for the normalizer/loader.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterator
from urllib.parse import urlparse

from ...exceptions import ConfigError, IngestionError
from ..base.extractor import BaseExtractor
from .duckdb import S3, resolve_location
from .excel_automation import extract_workbook, tables_to_records

logger = logging.getLogger("ingestion")


class ExcelAutomationExtractor(BaseExtractor):
    """Run the workbook automation engine and yield records for one table."""

    def __init__(
        self,
        config: Dict[str, Any] | None = None,
        *,
        source: str | None = None,
        output: str = "data",
        table: str | None = None,
        prefix: str | None = None,
        const: Dict[str, str] | None = None,
        data_start_row: int | None = None,
        table_markers: list[str] | None = None,
        profile: bool = False,
        relations: bool = False,
    ):
        super().__init__(dict(config or {}))
        self.source_ref = (
            source
            or self.config.get("source_file")
            or self.config.get("url")
            or self.config.get("excel_url")
        )
        self.output = str(output or "data").strip()
        self.table = str(table).strip() if table else None
        self.prefix = prefix
        self.const = dict(const or {})
        self.data_start_row = data_start_row
        self.table_markers = table_markers
        self.profile = profile
        self.relations = relations
        self.result: Any = None

    def _workbook_source(self) -> str | bytes:
        ref = str(self.source_ref or "").strip()
        if not ref:
            raise ConfigError("Missing workbook path/URL for ExcelAutomationExtractor")
        location = resolve_location(ref)
        if location.kind == "local":
            return location.uri
        if location.kind == S3:
            from .storage.minio_storage import MinioStorage

            parsed = urlparse(location.uri)
            storage = MinioStorage(self.config)
            if parsed.netloc:
                storage.bucket = parsed.netloc
            return storage.download_bytes((parsed.path or "").lstrip("/"))
        import requests

        response = requests.get(location.uri, timeout=120)
        response.raise_for_status()
        return response.content

    def _select_table(self, tables: Dict[str, Any]) -> str:
        if self.table:
            if self.table in tables:
                return self.table
            matches = [name for name in tables if name.endswith(f"_{self.table}")]
            if len(matches) == 1:
                return matches[0]
            raise ConfigError(
                f"Excel table {self.table!r} not found; available: {', '.join(tables)}"
            )
        if self.output in tables:
            return self.output
        matches = [name for name in tables if name.endswith(f"_{self.output}")]
        if len(matches) == 1:
            return matches[0]
        if matches:
            return matches[0]
        if len(tables) == 1:
            return next(iter(tables))
        raise ConfigError(
            f"Cannot select Excel output {self.output!r}; available: {', '.join(tables)}"
        )

    def extract(self) -> Iterator[Dict[str, Any]]:
        result = extract_workbook(
            self._workbook_source(),
            prefix=self.prefix,
            const=self.const,
            data_start_row=self.data_start_row,
            profile=self.profile,
            relations=self.relations,
            outputs=[self.output],
            table_markers=self.table_markers,
        )
        self.result = result
        records_by_table = tables_to_records(result.tables)
        if not records_by_table:
            raise IngestionError("Excel automation produced no tables")
        table = self._select_table(records_by_table)
        records = records_by_table[table]
        logger.info("Excel automation table '%s': %s records", table, len(records))
        if not records:
            raise IngestionError(f"Excel automation table '{table}' is empty")
        yield from records


__all__ = ["ExcelAutomationExtractor"]
