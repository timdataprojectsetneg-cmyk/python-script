"""SharePoint (Microsoft Graph) client.

Read-only access to the use case catalog workbook and Data Dictionary files.

A file reference is either:
- a **Graph item id**, resolved as ``sites/{SITE_ID}/drive/items/{FILE_ID}``
  (optionally forced with an ``id:`` prefix), or
- a **drive-relative path**, e.g. ``Folder/Available Data Source.xlsx``.

Path downloads fall back to a suffix match within the parent folder when the
exact path is missing (HTTP 404), so a file renamed with an ordinal prefix
(``1. File.xlsx`` matches ``File.xlsx``) still resolves.

Environment:

    SHAREPOINT__TENANT_ID
    SHAREPOINT__CLIENT_ID
    SHAREPOINT__CLIENT_SECRET
    SHAREPOINT__SITE_ID         e.g. telkomind.sharepoint.com,sites/SetnegTeam
    SHAREPOINT__FILE_ID         Graph drive item id of the catalog workbook (preferred)
    SHAREPOINT__CATALOG_FILE_ID legacy alias of SHAREPOINT__FILE_ID
    SHAREPOINT__CATALOG_PATH    fallback drive-relative path of the catalog workbook
    SHAREPOINT__DRIVE_ID        optional, used when SHAREPOINT__SITE_ID is not set
"""

from __future__ import annotations

import base64
import math
import re
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, quote, unquote, urlsplit

import requests

from ..config import get_raw
from ..exceptions import AuthError, ConfigError, ItemNotFound, SourceUnavailable

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
TOKEN_BASE = "https://login.microsoftonline.com"
DEFAULT_DICTIONARY_BASE_PATH = "Sitroom-2026/PROJECT/DATA/1 - Discover"

GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
OPAQUE_ID_RE = re.compile(r"^[A-Za-z0-9_\-!]{16,}$")
_ORDINAL_RE = re.compile(r"^\s*\d+[.)]\s+")
_COPY_SUFFIX_RE = re.compile(r"\s*\(\d+\)(?=\.[^./\\]*$|$)")
_NAV_SHEET_RE = re.compile(r"^15_\{00000000-0001-0000-([0-9A-Fa-f]{2})00-000000000000\}$")


def is_item_id(ref: str) -> bool:
    """Heuristic: a GUID or a long opaque token with no path/extension is an item id."""
    ref = (ref or "").strip()
    if not ref or any(ch in ref for ch in "/\\ ."):
        return False
    return bool(GUID_RE.match(ref) or OPAQUE_ID_RE.match(ref))


class SharePointClient:
    def __init__(self) -> None:
        self.tenant_id = get_raw("SHAREPOINT__TENANT_ID")
        self.client_id = get_raw("SHAREPOINT__CLIENT_ID")
        self.client_secret = get_raw("SHAREPOINT__CLIENT_SECRET")
        self.site_id = get_raw("SHAREPOINT__SITE_ID")
        self.drive_id = get_raw("SHAREPOINT__DRIVE_ID")
        self.file_id = get_raw("SHAREPOINT__FILE_ID")
        self.catalog_file_id = get_raw("SHAREPOINT__CATALOG_FILE_ID")
        self.catalog_path = get_raw("SHAREPOINT__CATALOG_PATH")
        self._token: str | None = None

    def _require(self, value: Any, name: str) -> str:
        if not value:
            raise ConfigError(f"Missing SharePoint configuration: {name}")
        return value

    def get_token(self) -> str:
        if self._token:
            return self._token
        tenant = self._require(self.tenant_id, "SHAREPOINT__TENANT_ID")
        data = {
            "client_id": self._require(self.client_id, "SHAREPOINT__CLIENT_ID"),
            "client_secret": self._require(self.client_secret, "SHAREPOINT__CLIENT_SECRET"),
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        try:
            resp = requests.post(
                f"{TOKEN_BASE}/{tenant}/oauth2/v2.0/token", data=data, timeout=30
            )
        except requests.RequestException as exc:
            raise SourceUnavailable(f"SharePoint token endpoint unreachable: {exc}") from exc
        if resp.status_code != 200:
            raise AuthError(f"SharePoint auth failed ({resp.status_code})")
        self._token = resp.json()["access_token"]
        return self._token

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.get_token()}"}

    def _fetch(self, url: str) -> bytes:
        resp = requests.get(url, headers=self._headers(), timeout=120)
        if resp.status_code == 401:
            raise AuthError("SharePoint download unauthorized")
        if resp.status_code == 404:
            raise ItemNotFound(f"SharePoint item not found: {url}")
        if resp.status_code >= 400:
            raise SourceUnavailable(f"SharePoint download failed ({resp.status_code})")
        return resp.content

    def item_url(self, file_id: str) -> str:
        """Graph URL for a drive item: ``sites/{SITE_ID}/drive/items/{FILE_ID}``."""
        file_id = self._require((file_id or "").strip(), "SHAREPOINT__FILE_ID")
        if self.site_id:
            return (
                f"{GRAPH_BASE}/sites/{self.site_id}"
                f"/drive/items/{quote(file_id, safe='')}"
            )
        drive = self._require(self.drive_id, "SHAREPOINT__SITE_ID or SHAREPOINT__DRIVE_ID")
        return f"{GRAPH_BASE}/drives/{quote(drive, safe='')}/items/{quote(file_id, safe='')}"

    def download_file_by_id(self, item_id: str, drive_id: str | None = None) -> bytes:
        """Download content using a Graph drive item id."""
        item_id = self._require((item_id or "").strip(), "item_id")
        if drive_id:
            url = f"{GRAPH_BASE}/drives/{quote(drive_id, safe='')}/items/{quote(item_id, safe='')}/content"
        else:
            url = f"{self.item_url(item_id)}/content"
        return self._fetch(url)

    def _children_url(self, folder_path: str) -> str:
        """Graph URL listing the children of a drive folder path ('' = root)."""
        folder_path = (folder_path or "").strip().strip("/")
        suffix = f":/{quote(folder_path)}:/children" if folder_path else "/children"
        if self.drive_id:
            root = f"{GRAPH_BASE}/drives/{quote(self.drive_id, safe='')}/root"
        else:
            site = self._require(self.site_id, "SHAREPOINT__SITE_ID")
            root = f"{GRAPH_BASE}/sites/{site}/drive/root"
        return root + suffix

    def list_children(self, folder_path: str) -> List[Dict[str, Any]]:
        """List drive items (``name``, ``id``, ``folder``/``file``) under a folder.

        Returns an empty list when the folder does not exist (HTTP 404).
        """
        url = f"{self._children_url(folder_path)}?$select=name,id,folder,file"
        resp = requests.get(url, headers=self._headers(), timeout=60)
        if resp.status_code == 404:
            return []
        if resp.status_code == 401:
            raise AuthError("SharePoint folder listing unauthorized")
        if resp.status_code >= 400:
            raise SourceUnavailable(
                f"SharePoint folder listing failed ({resp.status_code})"
            )
        return list((resp.json() or {}).get("value", []) or [])

    @staticmethod
    def _match_child(children: List[Dict[str, Any]], filename: str) -> Optional[Dict[str, Any]]:
        """Find a child matching ``filename``, tolerant of an ordinal prefix.

        Names are compared after ignoring an optional leading ordinal (``1. ``,
        ``2) ``) and a trailing copy suffix (`` (1)``), so a file renamed for
        ordering (``1. Foo.xlsx``) or by an upload copy (``Foo (1).xlsx``) still
        matches ``Foo.xlsx`` without updating the catalog. An exact name wins;
        otherwise the shortest equivalent name is chosen (deterministic on
        collisions).
        """
        def normalize(name: Any) -> str:
            text = _ORDINAL_RE.sub("", str(name).strip()).strip()
            return _COPY_SUFFIX_RE.sub("", text).strip().casefold()

        target = normalize(filename)
        if not target:
            return None
        matches = [child for child in children if normalize(child.get("name", "")) == target]
        if not matches:
            return None
        wanted = str(filename).strip().casefold()
        for child in matches:
            if str(child.get("name", "")).strip().casefold() == wanted:
                return child
        return min(matches, key=lambda child: len(str(child.get("name", ""))))

    def download_file(self, item_path: str) -> bytes:
        """Download content using a drive-relative path.

        If the exact path is missing (HTTP 404), fall back to matching a child of
        the parent folder whose name ends with the requested filename. This keeps
        downloads working after files are renamed with an ordinal prefix
        (e.g. ``1. Data Dictionary - ....xlsx``) without updating the catalog.
        """
        item_path = self._require((item_path or "").strip(), "item_path")
        if self.drive_id:
            url = f"{GRAPH_BASE}/drives/{quote(self.drive_id, safe='')}/root:/{quote(item_path)}:/content"
        else:
            site = self._require(self.site_id, "SHAREPOINT__SITE_ID")
            url = f"{GRAPH_BASE}/sites/{site}/drive/root:/{quote(item_path)}:/content"
        try:
            return self._fetch(url)
        except ItemNotFound:
            folder, _, filename = item_path.rpartition("/")
            if not filename:
                raise
            match = self._match_child(self.list_children(folder), filename)
            if match is None or not match.get("id"):
                raise
            return self.download_file_by_id(str(match["id"]))

    def get_content(self, ref: str) -> bytes:
        """Download by item id or path. ``id:`` prefix forces id interpretation."""
        ref = self._require((ref or "").strip(), "file reference")
        if ref.lower().startswith("id:"):
            return self.download_file_by_id(ref[3:].strip())
        if is_item_id(ref):
            return self.download_file_by_id(ref)
        return self.download_file(ref)

    def catalog_ref(self, override: str | None = None) -> str:
        """Resolve the catalog workbook reference.

        Precedence: override > SHAREPOINT__FILE_ID > SHAREPOINT__CATALOG_FILE_ID
        > SHAREPOINT__CATALOG_PATH > default.
        """
        return (
            override
            or self.file_id
            or self.catalog_file_id
            or self.catalog_path
            or "Available Data Source per Usecase.xlsx"
        )

    def dictionary_ref(self, name: str, sheet: str) -> Optional[str]:
        """Resolve a Data Dictionary file reference.

        Bare filenames are resolved under
        ``{SHAREPOINT__DICTIONARY_BASE_PATH}/Data Dictionary - {sheet}/{name}``,
        since the Data Dictionary folder differs per use case sheet. Item ids and
        explicit paths (containing ``/``) are returned unchanged.
        """
        name = (name or "").strip()
        if not name:
            return None
        if "/" in name or "\\" in name or name.lower().startswith("id:") or is_item_id(name):
            return name
        base = get_raw("SHAREPOINT__DICTIONARY_BASE_PATH", DEFAULT_DICTIONARY_BASE_PATH)
        base = (base or "").strip().strip("/")
        parts = [base] if base else []
        parts.append(f"Data Dictionary - {sheet}")
        parts.append(name)
        return "/".join(parts)

    @staticmethod
    def share_url_to_path(url: str) -> Optional[str]:
        """Decode a SharePoint share URL into a drive-relative path.

        ``.../Shared Documents/<path>`` (or ``/Documents/<path>``) becomes
        ``<path>`` with the leading slash stripped, since the site default library
        root is the shared documents library. Returns ``None`` when the URL has no
        known library marker.
        """
        if not url or "://" not in url:
            return None
        path = unquote(urlsplit(url).path)
        for marker in ("/Shared Documents/", "/Documents/"):
            idx = path.lower().find(marker.lower())
            if idx != -1:
                return path[idx + len(marker):].strip("/") or None
        return None

    def resolve_share_url(self, url: str) -> Optional[str]:
        """Resolve a share URL to an ``id:`` ref via the Graph ``/shares`` API.

        Used when the URL cannot be decoded into a drive path. Returns ``None`` on
        any error (HTTP >= 400) so the caller can fall back.
        """
        if not url or "://" not in url:
            return None
        token = base64.urlsafe_b64encode(url.encode("utf-8")).decode("ascii").rstrip("=")
        api = f"{GRAPH_BASE}/shares/u!{token}/driveItem?$select=id,name,parentReference"
        resp = requests.get(api, headers=self._headers(), timeout=30)
        if resp.status_code >= 400:
            return None
        item_id = (resp.json() or {}).get("id")
        return f"id:{item_id}" if item_id else None

    def resolve_dictionary_link(self, link: str, sheet: str) -> Optional[str]:
        """Resolve a Data Dictionary hyperlink to a file reference.

        A hyperlink is preferred over the cell text because the text is only a
        display name. Non-URL values are treated as an item id or explicit path,
        else resolved as a bare filename via :meth:`dictionary_ref`. URLs are
        decoded to a drive path first, then resolved via the Graph ``/shares`` API.
        """
        link = (link or "").strip()
        if not link:
            return None
        if "://" not in link:
            return link if (is_item_id(link) or "/" in link) else self.dictionary_ref(link, sheet)
        return self.share_url_to_path(link) or self.resolve_share_url(link)

    @staticmethod
    def link_sheet_hint(url: str) -> Optional[int]:
        """Best-effort 0-based sheet index encoded in a share URL's ``nav`` anchor.

        Section links created from the Excel viewer carry a ``nav`` token whose
        decoded GUID encodes the target sheet ordinal (e.g. ``…-0300-…`` -> sheet
        index 2). Returns ``None`` when the anchor is absent or not in that form,
        so callers can fall back to name matching.
        """
        if not url or "://" not in url:
            return None
        nav = (parse_qs(urlsplit(url).query).get("nav") or [None])[0]
        if not nav:
            return None
        try:
            decoded = base64.b64decode(nav + "=" * (-len(nav) % 4)).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return None
        match = _NAV_SHEET_RE.match(decoded)
        if not match:
            return None
        return int(match.group(1), 16) - 1

    def list_sheets(self, ref: str) -> List[str]:
        from io import BytesIO

        import pandas as pd

        excel = pd.ExcelFile(BytesIO(self.get_content(ref)), engine="openpyxl")
        return list(excel.sheet_names)

    @staticmethod
    def _open_sheet(workbook: Any, sheet: Any) -> Any:
        if isinstance(sheet, str) and sheet in workbook.sheetnames:
            return workbook[sheet]
        if isinstance(sheet, int):
            return workbook.worksheets[sheet]
        if isinstance(sheet, str) and sheet.isdigit():
            return workbook.worksheets[int(sheet)]
        return workbook.worksheets[0]

    def _load_matrix(self, ref: str, sheet: Any) -> tuple[List[List[Any]], List[Dict[int, str]]]:
        from io import BytesIO

        from openpyxl import load_workbook

        workbook = load_workbook(BytesIO(self.get_content(ref)), data_only=True)
        worksheet = self._open_sheet(workbook, sheet)

        matrix: List[List[Any]] = []
        links: List[Dict[int, str]] = []
        for row in worksheet.iter_rows():
            values: List[Any] = []
            row_links: Dict[int, str] = {}
            for cell in row:
                values.append(cell.value)
                target = getattr(getattr(cell, "hyperlink", None), "target", None)
                if target:
                    row_links[cell.column - 1] = target
            matrix.append(values)
            links.append(row_links)
        return matrix, links

    def read_matrix(self, ref: str, sheet: Any) -> List[List[Any]]:
        """Return a sheet as a raw matrix of cell values (row-major)."""
        matrix, _ = self._load_matrix(ref, sheet)
        return matrix

    def read_sheet(
        self, ref: str, sheet: Any, header_hints: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Read a sheet to records, locating the header row dynamically.

        Catalog sheets often start with title/blank rows and use a two-row header;
        ``header_hints`` (e.g. ``["Source Name"]``) locate the header row, and blank
        header cells are filled from the row below. Cell hyperlinks (e.g. the
        "Data Dictionary" edit link) are captured under ``_links``.
        """
        matrix, links = self._load_matrix(ref, sheet)
        return self._matrix_to_records(matrix, header_hints or [], links)

    @staticmethod
    def _is_blank(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, float) and math.isnan(value):
            return True
        if isinstance(value, str) and value.strip().lower() in ("", "nan", "none"):
            return True
        return False

    @staticmethod
    def _norm_cell(value: Any) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())

    def _detect_header_row(self, matrix: List[List[Any]], hints: List[str]) -> int:
        wanted = [self._norm_cell(hint) for hint in hints if hint]
        if not wanted:
            return 0
        for index, row in enumerate(matrix):
            cells = [self._norm_cell(cell) for cell in row]
            if any(any(hint in cell for cell in cells) for hint in wanted):
                return index
        return 0

    def _matrix_to_records(
        self,
        matrix: List[List[Any]],
        hints: List[str],
        links: Optional[List[Dict[int, str]]] = None,
    ) -> List[Dict[str, Any]]:
        if not matrix:
            return []
        links = links or []

        header_index = self._detect_header_row(matrix, hints)
        header = list(matrix[header_index])
        sub = matrix[header_index + 1] if header_index + 1 < len(matrix) else []

        names: List[str] = []
        used_sub = False
        for index, cell in enumerate(header):
            if self._is_blank(cell) and index < len(sub) and not self._is_blank(sub[index]):
                names.append(str(sub[index]).strip())
                used_sub = True
            elif self._is_blank(cell):
                names.append(f"col_{index}")
            else:
                names.append(str(cell).strip())

        data_start = header_index + 2 if used_sub else header_index + 1
        records: List[Dict[str, Any]] = []
        for offset, row in enumerate(matrix[data_start:]):
            if all(self._is_blank(cell) for cell in row):
                continue
            record = {
                names[index] if index < len(names) else f"col_{index}": (
                    None if self._is_blank(value) else value
                )
                for index, value in enumerate(row)
            }
            if all(value is None for value in record.values()):
                continue

            row_links = links[data_start + offset] if data_start + offset < len(links) else {}
            record["_links"] = {
                names[index]: url for index, url in row_links.items() if index < len(names)
            }
            records.append(record)
        return records


    def read_sheets(self, ref: str) -> Dict[str, List[Dict[str, Any]]]:
        """Read every sheet of a workbook, keyed by sheet name."""
        from io import BytesIO

        import pandas as pd

        frames = pd.read_excel(
            BytesIO(self.get_content(ref)), sheet_name=None, engine="openpyxl"
        )
        return {name: frame.to_dict(orient="records") for name, frame in frames.items()}
