"""Read Google Sheets using a service-account credentials JSON file.

The client intentionally exposes the same small interface as ``SharePointClient``
so catalog parsing and scaffolding can use either document source unchanged.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlsplit

from ..config import get_raw
from ..exceptions import ConfigError, SourceUnavailable


class SpreadsheetClient:
    def __init__(self) -> None:
        self.credentials_file = get_raw(
            "SPREADSHEET__CREDENTIALS_JSON",
            get_raw("GOOGLE_APPLICATION_CREDENTIALS", "glossy-fastness-511414-p4-64cb764cfc18.json"),
        )
        self.spreadsheet_id = get_raw(
            "SPREADSHEET__FILE_ID",
            get_raw("SPREADSHEET__ID", get_raw("GOOGLE__SPREADSHEET_ID")),
        )
        self._service = None

    @staticmethod
    def _spreadsheet_id(ref: str) -> str:
        ref = (ref or "").strip()
        match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", ref)
        if match:
            return match.group(1)
        return ref

    def _api(self) -> Any:
        if self._service is not None:
            return self._service
        if not self.credentials_file:
            raise ConfigError("Missing SPREADSHEET__CREDENTIALS_JSON")
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
            )
            self._service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
            return self._service
        except Exception as exc:  # noqa: BLE001
            raise SourceUnavailable(f"Google Sheets client initialization failed: {exc}") from exc

    def catalog_ref(self, override: str | None = None) -> str:
        ref = override or self.spreadsheet_id
        if not ref:
            raise ConfigError("Missing SPREADSHEET__FILE_ID (or GOOGLE__SPREADSHEET_ID)")
        return self._spreadsheet_id(ref)

    def dictionary_ref(self, name: str, sheet: str) -> Optional[str]:
        # Bare dictionary names refer to tabs in the catalog workbook. A URL/ID
        # can point at a separate workbook, matching SharePoint's file links.
        value = (name or "").strip()
        if not value:
            return None
        if "/spreadsheets/d/" in value or re.fullmatch(r"[A-Za-z0-9_-]{20,}", value):
            return value
        return self.spreadsheet_id

    def resolve_dictionary_link(self, link: str, sheet: str) -> Optional[str]:
        """Resolve a Data Dictionary hyperlink to a workbook reference.

        Google Sheets hyperlinks point at a workbook URL (``/spreadsheets/d/<id>``);
        bare ids and names fall back to :meth:`dictionary_ref` so tabs of the
        catalog workbook keep working.
        """
        value = (link or "").strip()
        if not value:
            return None
        if "/spreadsheets/d/" in value:
            return self._spreadsheet_id(value)
        if re.fullmatch(r"[A-Za-z0-9_-]{20,}", value):
            return value
        return self.dictionary_ref(value, sheet)

    def link_sheet_hint(self, url: str) -> Optional[int]:
        """Map a share URL's ``gid`` (tab sheetId) to its 0-based tab index.

        Google Sheets links carry ``#gid=<sheetId>``; the catalog selection treats
        the hint as a tab index, so the workbook metadata is consulted. Returns
        ``None`` when the link has no gid or the tab is unknown.
        """
        if not url or "/spreadsheets/d/" not in url:
            return None
        parts = urlsplit(url)
        gid = (parse_qs(parts.query).get("gid") or parse_qs(parts.fragment).get("gid") or [None])[0]
        if gid is None:
            return None
        try:
            wanted = int(gid)
        except (TypeError, ValueError):
            return None
        fields = "sheets(properties(sheetId,index))"
        try:
            meta = self._api().spreadsheets().get(
                spreadsheetId=self._spreadsheet_id(url), fields=fields
            ).execute()
        except Exception:  # noqa: BLE001 - best-effort hint; caller falls back
            return None
        for sheet in meta.get("sheets", []):
            props = sheet.get("properties", {})
            if props.get("sheetId") == wanted:
                return props.get("index")
        return None

    def _metadata(self, ref: str) -> Dict[str, Any]:
        return self._api().spreadsheets().get(
            spreadsheetId=self._spreadsheet_id(ref), fields="sheets(properties(title,index))"
        ).execute()

    def list_sheets(self, ref: str) -> List[str]:
        return [s["properties"]["title"] for s in self._metadata(ref).get("sheets", [])]

    def read_matrix(self, ref: str, sheet: Any) -> List[List[Any]]:
        title = str(sheet)
        response = self._api().spreadsheets().values().get(
            spreadsheetId=self._spreadsheet_id(ref), range=f"'{title.replace(chr(39), chr(39) * 2)}'!A:ZZ"
        ).execute()
        return response.get("values", [])

    def _row_links(self, ref: str, sheet: Any) -> List[Dict[int, str]]:
        """Cell hyperlinks per row (column index -> URL) for a sheet range."""
        title = str(sheet).replace("'", "''")
        fields = "sheets(data(rowData(values(hyperlink,userEnteredFormat.textFormat.link))))"
        response = self._api().spreadsheets().get(
            spreadsheetId=self._spreadsheet_id(ref),
            ranges=[f"'{title}'!A:ZZ"],
            includeGridData=True,
            fields=fields,
        ).execute()
        links: List[Dict[int, str]] = []
        for sheet_data in response.get("sheets", []):
            for block in sheet_data.get("data", []) or []:
                for row in block.get("rowData", []) or []:
                    row_links: Dict[int, str] = {}
                    for col, cell in enumerate(row.get("values", []) or []):
                        text_format = cell.get("userEnteredFormat", {}).get("textFormat", {}) or {}
                        url = cell.get("hyperlink") or (text_format.get("link", {}) or {}).get("uri")
                        if url:
                            row_links[col] = url
                    links.append(row_links)
        return links

    def read_sheet(self, ref: str, sheet: Any, header_hints: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        matrix = self.read_matrix(ref, sheet)
        if not matrix:
            return []
        links = self._row_links(ref, sheet)
        hints = [str(h).lower() for h in (header_hints or [])]
        header_index = next((i for i, row in enumerate(matrix) if any(h in str(c).lower() for c in row for h in hints)), 0)
        header = matrix[header_index]
        sub = matrix[header_index + 1] if header_index + 1 < len(matrix) else []
        names = [str(c).strip() if c not in (None, "") else (str(sub[i]).strip() if i < len(sub) and sub[i] not in (None, "") else f"col_{i}") for i, c in enumerate(header)]
        start = header_index + 2 if any(c in (None, "") for c in header) and sub else header_index + 1
        records: List[Dict[str, Any]] = []
        for offset, row in enumerate(matrix[start:]):
            if not any(value not in (None, "") for value in row):
                continue
            record = {
                names[i] if i < len(names) else f"col_{i}": value
                for i, value in enumerate(row)
                if value not in (None, "")
            }
            index = start + offset
            row_links = links[index] if index < len(links) else {}
            record["_links"] = {
                names[i]: url for i, url in row_links.items() if i < len(names)
            }
            records.append(record)
        return records
