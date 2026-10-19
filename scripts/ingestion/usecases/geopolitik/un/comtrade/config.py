"""Configuration for UN Comtrade Ingestion."""

import os
from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://comtradeplus.un.org/TradeFlow",
    "api_url": "https://comtradeapi.un.org/public/v1/preview/C/A/HS",
    "subscription_key": os.environ.get("GEOPOLITIK__UN__COMTRADE__PRIMARY_KEY", ""),
    "max_records": 50,
    "timeout": 20,
}
