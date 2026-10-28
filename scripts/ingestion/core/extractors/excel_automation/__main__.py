"""``python -m ingestion.core.extractors.excel_automation`` entry point."""

from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"ERROR: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        raise
