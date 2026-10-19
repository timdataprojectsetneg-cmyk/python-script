"""Configuration for BPS Profil Sosioekonomi Ingestion."""

import os
from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/26/key/WebAPI_KEY/",
    "base_url": "https://webapi.bps.go.id/",
    "api_key": os.environ.get("BPS_API_KEY", "a7e713042542d805ed3960836090e888"),
    "max_records": 50,
    "timeout": 20,
}
