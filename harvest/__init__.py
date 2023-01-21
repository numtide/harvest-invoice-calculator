#!/usr/bin/env python3

from typing import Any, Dict, List

from rest import http_request


def get_time_entries(
    account_id: str, access_token: str, from_date: int, to_date: int
) -> List[Dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Harvest-Account-id": account_id,
    }
    url = f"https://api.harvestapp.com/v2/time_entries?from={from_date}&to={to_date}"
    entries = []
    while url is not None:
        resp = http_request(
            url,
            headers=headers,
        )
        entries.extend(resp["time_entries"])
        url = resp["links"]["next"]
    return entries
