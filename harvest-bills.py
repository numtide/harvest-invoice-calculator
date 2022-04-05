#!/usr/bin/env python3

from collections import defaultdict
import urllib.request
import json
import os
import sys
from typing import Dict, Optional, Any, List
from fractions import Fraction
from dataclasses import dataclass


# curl
# "" \
#  -H  \
#  -H "Harvest-Account-Id: $ACCOUNT_ID" \
#  -H "User-Agent: MyApp (yourname@example.com)"


def rest_request(
    url: str, method: str = "GET", headers={}, data: Optional[bytes] = None
) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers=headers, method=method, data=data)
    resp = urllib.request.urlopen(req)
    return json.load(resp)


def get_time_entries(
    account_id: str, access_token: str, from_date: int, to_date: int
) -> List[Dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Harvest-Account-id": account_id,
        "User-Agent": "Numtide invoice generator",
    }
    url = f"https://api.harvestapp.com/v2/time_entries?from={from_date}&to={to_date}"
    entries = []
    while url is not None:
        resp = rest_request(
            url,
            headers=headers,
        )
        entries.extend(resp["time_entries"])
        url = resp["links"]["next"]
    return entries


@dataclass
class Project:
    # Use fractions here to avoid rounding errors, round to cents once on export
    rounded_hours: Fraction = Fraction(0)
    original_cost: Fraction = Fraction(0)
    original_currency: str = ""
    converted_cost: Fraction = Fraction(0)
    converted_currency: str = ""


def round_cents(n: Fraction) -> float:
    return float(round(n, 2))


Aggregated = Dict[str, Dict[str, Project]]


def aggregate_time_entries(entries: List[Dict[str, Any]]) -> Aggregated:
    by_user_and_project: Dict[str, Dict[str, Project]] = defaultdict(
        lambda: defaultdict(lambda: Project())
    )
    for entry in entries:
        client_name = entry["client"]["name"]
        project = by_user_and_project[entry["user"]["name"]][client_name]
        project.rounded_hours += Fraction(entry["rounded_hours"])
        if project.original_currency == "":
            project.original_currency = entry["client"]["currency"]
        else:
            msg = f"Currency of customer changed from {project.original_currency} to {entry['client']['currency']} within the billing period. This is not supported!"
            assert project.original_currency == entry["client"]["currency"], msg
        rate = entry["task_assignment"]["hourly_rate"]
        if rate == 0:
            print(
                f"WARNING, hourly rate for {client_name}/{entry['task']['name']} is 0.0"
            )
        project.original_cost += Fraction(entry["rounded_hours"]) * Fraction(rate)
    return by_user_and_project


# curl -X POST https://api.transferwise.com/v3/quotes/ -H 'Content-type: application/json' -d '{   "sourceCurrency": "GBP",    "targetCurrency": "USD",    "sourceAmount": null,    "targetAmount": 110}' | jq


def convert_currencies(aggregated: Aggregated) -> Aggregated:
    return aggregated


def main() -> None:
    account_id = os.environ.get("HARVEST_ACCOUNT_ID")
    if account_id is None:
        print(
            "HARVEST_ACCOUNT_ID not set, get one from https://id.getharvest.com/developers",
            file=sys.stderr,
        )
        sys.exit(1)
    access_token = os.environ.get("HARVEST_BEARER_TOKEN")
    if access_token is None:
        print(
            "HARVEST_BEARER_TOKEN not set, get one from https://id.getharvest.com/developers",
            file=sys.stderr,
        )
        sys.exit(1)
    entries = get_time_entries(account_id, access_token, 20220101, 20220131)

    by_user_and_project = convert_currencies(aggregate_time_entries(entries))

    for user, projects in by_user_and_project.items():
        print(f"{user}:")
        for project_name, project in projects.items():
            cost = round_cents(project.original_cost)
            print(
                f"  {project_name}: {float(project.rounded_hours)} / {cost} {project.original_currency}"
            )


# curl -X POST \                                                                                                                                                                                                                 ✘ 23|3 jfroche@marcel 18:26:47
#  https://api.transferwise.com/v3/quotes/ \
#  -H 'Content-type: application/json' \
#  -d '{
#    "sourceCurrency": "GBP",
#    "targetCurrency": "EUR",
#    "sourceAmount": 1000,
#    "targetAmount": null
# }' | jq '.paymentOptions[] | select(.payIn == "BANK_TRANSFER" and .payOut == "BANK_TRANSFER") | .targetAmount, .fee.transferwise'

if __name__ == "__main__":
    main()
