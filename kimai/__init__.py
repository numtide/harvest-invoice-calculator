#!/usr/bin/env python3

from datetime import datetime
from typing import Any, Dict, List

from rest import http_request2


def kimai_request(url: str, access_token: str, data: Dict[str, Any]) -> Dict[str, Any]:
    data["page"] = 1
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    all_entries = []
    while True:
        resp = http_request2(url, headers=headers, data=data)
        all_entries.extend(resp.json)

        total_pages = int(resp.headers.get("X-Total-Pages", 1))
        if data["page"] >= total_pages:
            break

        data["page"] += 1

    return all_entries


def get_visible_projects(access_token: str) -> List[Dict[str, Any]]:

    url = "http://127.0.0.1:8001/api/projects"
    data = {
        "visible": 1,
    }

    return kimai_request(url, access_token, data)


def get_visible_users(access_token: str) -> List[Dict[str, Any]]:

    url = "http://127.0.0.1:8001/api/users"
    data = {
        "visible": 1,
    }

    return kimai_request(url, access_token, data)


def get_time_entries(
    access_token: str,
    from_date: datetime,
    to_date: datetime,
    user_id: int,
    customer_id: int,
) -> List[Dict[str, Any]]:

    url = "http://127.0.0.1:8001/api/timesheets"
    data = {
        "user": user_id,
        "customer": customer_id,
        "begin": from_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "end": to_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "billable": 1,
    }
    return kimai_request(url, access_token, data)
