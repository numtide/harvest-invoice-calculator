#!/usr/bin/env python3

import urllib.request
import json
import os
import sys
from typing import Dict, Optional, Any


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


def get_time_reports(
    account_id: str, access_token: str, from_date: int, to_date: int
) -> None:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Harvest-Account-id": account_id,
        "User-Agent": "Numtide invoice generator",
    }
    resp = rest_request(
        f"https://api.harvestapp.com/v2/reports/time/clients?from={from_date}&to={to_date}",
        headers=headers,
    )
    breakpoint()


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
    get_time_reports(account_id, access_token, 20220101, 20220131)


# curl -X POST https://api.transferwise.com/v3/quotes/ -H 'Content-type: application/json' -d '{   "sourceCurrency": "GBP",    "targetCurrency": "USD",    "sourceAmount": null,    "targetAmount": 110}' | jq


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
