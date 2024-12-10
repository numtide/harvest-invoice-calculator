#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from kimai.data import (
    ActivityInfo,
    CustomerInfo,
    TimeEntryFull,
    UserInfo,
)
from rest import http_request2


@dataclass
class KimaiAPI:
    access_token: str
    api_url: str

    def kimai_request(
        self, endpoint: str, data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        data["page"] = 1
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        all_entries = []
        while True:
            url = f"{self.api_url}{endpoint}"
            resp = http_request2(url, headers=headers, data=data)
            if isinstance(resp.json, dict):
                all_entries.append(resp.json)
            else:
                all_entries.extend(resp.json)

            total_pages = int(resp.headers.get("X-Total-Pages", 1))
            if data["page"] >= total_pages:
                break

            data["page"] += 1

        return all_entries

    def get_visible_projects(self, billable: bool = False) -> list[dict[str, Any]]:
        endpoint = "/api/projects"
        data = {
            "visible": 1,
        }
        return self.kimai_request(endpoint, data)

    def get_visible_users(self) -> list[dict[str, Any]]:
        endpoint = "/api/users"
        data = {
            "visible": 1,
        }
        return self.kimai_request(endpoint, data)

    def get_customer(self, id: int) -> CustomerInfo:
        endpoint = f"/api/customers/{id}"
        custom_data = self.kimai_request(endpoint, {})
        return CustomerInfo.from_json(custom_data[0])

    def get_user(self, id: int) -> UserInfo:
        endpoint = f"/api/users/{id}"
        user_data = self.kimai_request(endpoint, {})
        return UserInfo.from_json(user_data[0])

    def get_activity(self, id: int) -> ActivityInfo:
        endpoint = f"/api/activities/{id}"
        activity_data = self.kimai_request(endpoint, {})
        return ActivityInfo.from_json(activity_data[0])

    def get_time_entries(
        self,
        from_date: datetime,
        to_date: datetime,
        user_id: int,
        customer_id: int,
        billable: bool = True,
    ) -> list[dict[str, Any]]:
        endpoint = "/api/timesheets"
        data = {
            "user": user_id,
            "customer": customer_id,
            "begin": from_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": to_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "billable": int(billable),
        }
        return self.kimai_request(endpoint, data)

    def get_time_entry(self, id: int) -> TimeEntryFull:
        endpoint = f"/api/timesheets/{id}"
        entry_data = self.kimai_request(endpoint, {})
        return TimeEntryFull.from_json(entry_data[0])
