"""Notifikasi ePing: WTO SPS/TBT notifications from the public ePing search API.

Endpoint: ``https://epingalert.org/api/v1/azureSearch/getAll`` (the API behind the ePing
search page). Pages are fetched newest-first from ``distributionDateFrom`` (default: last
``LOOKBACK_DAYS`` days; ``0`` = whole history). Pagination is followed until ``totalCount``
is reached. Optional keys: ``DOMAIN_IDS`` (1=TBT, 2=SPS, comma separated;
default both), ``DISTRIBUTION_DATE_FROM`` (YYYY-MM-DD), ``LOOKBACK_DAYS`` (default 30),
``PAGE_SIZE`` (default 100), ``MAX_PAGES`` (default unlimited; debug cap), ``LANGUAGE`` (default 1 = English).
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import parse_qsl, urlsplit

from .....config import get as env_get
from .....core.base.extractor import BaseExtractor
from .....exceptions import SourceUnavailable
from .config import PUBLISHER, SOURCE

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://epingalert.org/api/v1/azureSearch/getAll"
DEFAULT_LOOKBACK_DAYS = 30
DEFAULT_PAGE_SIZE = 100


def _names(items: Any) -> Optional[str]:
    if not items:
        return None
    parts = [str(i.get("name")).strip() for i in items if isinstance(i, dict) and i.get("name")]
    return "; ".join(parts) or None


def _date(value: Any) -> Optional[str]:
    return str(value)[:10] if value else None


def _text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def parse_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Map one ePing API item to the dictionary field names."""
    return {
        "id": _text(item.get("id")),
        "area": _text(item.get("area")),
        "notificationtype": _text(item.get("notificationType")),
        "distributiondate": _date(item.get("distributionDate")),
        "commentdeadlinedate": _date(item.get("commentDeadlineDate")),
        "proposedadoptiondate": _date(item.get("proposedAdoptionDate")),
        "proposedentryintoforcedate": _date(item.get("proposedEntryIntoForceDate")),
        "documentsymbol": _text(item.get("documentSymbol")),
        "notifyingmember": _text(item.get("notifyingMember")),
        "notifyingmembercode": _text(item.get("notifyingMemberCode")),
        "titleplain": _text(item.get("titlePlain")),
        "descriptionplain": _text(item.get("descriptionPlain")),
        "productsfreetextplain": _text(item.get("productsFreeTextPlain")),
        "hscodetext": _text(item.get("hsCodeText")),
        "icscodetext": _text(item.get("icsCodeText")),
        "keywords": _names(item.get("keywords")),
        "objectives": _names(item.get("objectives")),
        "alltradingpartners": item.get("allTradingPartners"),
        "countriesaffected": _names(item.get("countriesAffected")),
        "conformstandardyes": item.get("conformStandardYes"),
        "tradefacilitatingmeasure": item.get("tradeFacilitatingMeasure"),
        "parentid": item.get("parentId"),
        "linktonotification": _text(item.get("linkToNotification")),
        "notifieddocumentlink": _text(item.get("notifiedDocumentLink")),
    }


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = (config.get("url") or DEFAULT_URL).split("?")[0]
        self.url_query = dict(parse_qsl(urlsplit(config.get("url") or "").query))
        self.page_size = int(self._opt("page_size", DEFAULT_PAGE_SIZE))
        max_pages = int(self._opt("max_pages", 0))
        self.max_pages = max_pages if max_pages > 0 else None

    def _opt(self, key: str, default: Any = None) -> Any:
        value = self.config.get(key.lower())
        if value in (None, ""):
            value = env_get(self.config.get("usecase", "geopolitik"), PUBLISHER, SOURCE, key.upper())
        return default if value in (None, "") else value

    def build_params(self, page: int) -> Dict[str, Any]:
        """Query params; the date window comes from DISTRIBUTION_DATE_FROM, else LOOKBACK_DAYS."""
        date_from = self._opt("distribution_date_from")
        if not date_from and self._opt("lookback_days") is None:
            date_from = self.url_query.get("distributionDateFrom")
        if not date_from:
            days = int(self._opt("lookback_days", DEFAULT_LOOKBACK_DAYS))
            if days > 0:
                date_from = (date.today() - timedelta(days=days)).isoformat()
        params: Dict[str, Any] = {
            "page": page,
            "pageSize": self.page_size,
            "sortBy": "distributionDate",
            "sortDirection": "desc",
            "language": self._opt("language", self.url_query.get("language", 1)),
        }
        if date_from:
            params["distributionDateFrom"] = date_from
        domains = self._opt("domain_ids") or self.url_query.get("domainIds")
        if domains:
            params["domainIds"] = [d.strip() for d in str(domains).split(",") if d.strip()]
        return params

    def extract(self) -> Iterator[Dict[str, Any]]:
        yielded = 0
        page = 0
        while self.max_pages is None or page < self.max_pages:
            page += 1
            resp = self.http.get(
                self.base_url,
                params=self.build_params(page),
                headers={"Accept": "application/json"},
                timeout=60,
            )
            try:
                payload = resp.json()
            except ValueError as exc:
                raise SourceUnavailable(f"ePing returned non-JSON response: {exc}") from exc
            if "items" not in payload:
                raise SourceUnavailable("ePing response has no 'items' (API contract changed?)")
            items: List[Dict[str, Any]] = payload.get("items") or []
            for item in items:
                yielded += 1
                yield parse_item(item)
            total = int(payload.get("totalCount") or 0)
            if not items or page * self.page_size >= total:
                return
        logger.warning(
            "ePing: stopped at MAX_PAGES=%s (%s rows); unset MAX_PAGES to fetch the rest", self.max_pages, yielded
        )
