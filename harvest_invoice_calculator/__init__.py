#!/usr/bin/env python3

from collections import defaultdict
import urllib.request
import json
import os
import csv
import sys
from datetime import datetime, date
import calendar
import functools
import argparse
from typing import Dict, Optional, Any, List
from fractions import Fraction
from dataclasses import dataclass


def http_request(
    url: str,
    method: str = "GET",
    headers: Dict[str, str] = {},
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    body = None
    if data:
        body = json.dumps(data).encode("ascii")
    headers = headers.copy()
    headers["User-Agent"] = "Numtide invoice generator"
    req = urllib.request.Request(url, headers=headers, method=method, data=body)
    resp = urllib.request.urlopen(req)
    return json.load(resp)


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


@functools.cache
def exchange_rate(source: str, target: str) -> Fraction:
    data = dict(sourceCurrency=source, targetCurrency=target)
    resp = http_request(
        "https://api.transferwise.com/v3/quotes/",
        method="POST",
        data=data,
        headers={"Content-type": "application/json"},
    )
    return Fraction(resp["rate"])


def convert_cost(project: "Project", target_currency: str) -> Fraction:
    rate = exchange_rate(project.currency, target_currency)
    numtide_rate = Fraction(0.8)
    return project.cost * rate * numtide_rate


@dataclass
class Project:
    # Use fractions here to avoid rounding errors, round to cents once on export
    rounded_hours: Fraction = Fraction(0)
    cost: Fraction = Fraction(0)
    currency: str = ""

    def converted_cost(self, currency: str) -> Fraction:
        return convert_cost(self, currency)


def round_cents(n: Fraction) -> float:
    """
    Use this method only for displaying currencies to avoid rounding errors
    """
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
        if project.currency == "":
            project.currency = entry["client"]["currency"]
        else:
            msg = f"Currency of customer changed from {project.currency} to {entry['client']['currency']} within the billing period. This is not supported!"
            assert project.currency == entry["client"]["currency"], msg
        rate = entry["task_assignment"]["hourly_rate"]
        if rate == 0:
            print(
                f"WARNING, hourly rate for {client_name}/{entry['task']['name']} is 0.0"
            )
        project.cost += Fraction(entry["rounded_hours"]) * Fraction(rate)
    return by_user_and_project


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    account = os.environ.get("HARVEST_ACCOUNT_ID")
    parser.add_argument(
        "--harvest-account-id",
        default=account,
        required=account is None,
        help="Get one from https://id.getharvest.com/developers",
    )
    token = os.environ.get("HARVEST_BEARER_TOKEN")
    parser.add_argument(
        "--harvest-bearer-token",
        default=os.environ.get("HARVEST_BEARER_TOKEN"),
        required=token is None,
        help="Get one from https://id.getharvest.com/developers",
    )
    parser.add_argument(
        "--user",
        type=str,
        help="user to filter for",
    )
    parser.add_argument(
        "--start",
        type=int,
        help="Start date i.e. 20220101",
    )
    parser.add_argument(
        "--end",
        type=int,
        help="End date i.e. 20220101",
    )
    parser.add_argument(
        "--month",
        type=int,
        choices=range(1, 13),
        help="Month to generate report for (conflicts with `--start` and `--end`)",
    )
    parser.add_argument(
        "--currency",
        default="EUR",
        type=str,
        help="Target currency to convert to, i.e EUR",
    )
    parser.add_argument(
        "--format",
        default="humanreadable",
        choices=("humanreadable", "csv", "json"),
        type=str,
        help="Output format",
    )
    args = parser.parse_args()
    today = datetime.today()
    if args.month and (args.start or args.end):
        print("--month flag conflicts with --start and --end", file=sys.stderr)
        sys.exit(1)
    if args.month:
        first_day, last_day = calendar.monthrange(today.year, args.month)
        args.start = date(today.year, args.month, first_day).strftime("%Y%m%d")
        args.end = date(today.year, args.month, last_day).strftime("%Y%m%d")
    elif (args.start and not args.end) or (args.end and not args.start):
        print("both --start and --end flag must be passed", file=sys.stderr)
        sys.exit(1)
    elif not args.start and not args.end:
        start_of_month = today.replace(day=1)
        args.start = start_of_month.strftime("%Y%m%d")
        args.end = today.strftime("%Y%m%d")

    return args


def print_humanreadable(by_user_and_project: Aggregated, currency: str) -> None:
    for user, projects in by_user_and_project.items():
        print(f"{user}:")
        for project_name, project in projects.items():
            cost = round_cents(project.cost)
            converted_cost = round_cents(project.converted_cost(currency))

            print(
                f"  {project_name}: {float(project.rounded_hours)}h, {cost} {project.currency} -> {converted_cost} {currency}"
            )


def print_csv(by_user_and_project: Aggregated, currency: str) -> None:
    fieldnames = [
        "user",
        "project",
        "rounded_hours",
        "source_cost",
        "source_currency",
        "target_cost",
        "target_currency",
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for user, projects in by_user_and_project.items():
        for project_name, project in projects.items():
            writer.writerow(
                dict(
                    user=user,
                    project=project_name,
                    rounded_hours=float(project.rounded_hours),
                    source_cost=round_cents(project.cost),
                    source_currency=project.currency,
                    target_cost=round_cents(project.converted_cost(currency)),
                    target_currency=currency,
                )
            )


def print_json(by_user_and_project: Aggregated, currency: str) -> None:
    data = []
    for user, projects in by_user_and_project.items():
        for project_name, project in projects.items():
            data.append(
                dict(
                    user=user,
                    project=project_name,
                    rounded_hours=float(project.rounded_hours),
                    source_cost=round_cents(project.cost),
                    source_currency=project.currency,
                    target_cost=round_cents(project.converted_cost(currency)),
                    target_currency=currency,
                )
            )
    json.dump(data, sys.stdout, indent=4, sort_keys=True)


def main() -> None:
    args = parse_args()
    entries = get_time_entries(
        args.harvest_account_id, args.harvest_bearer_token, args.start, args.end
    )

    by_user_and_project = aggregate_time_entries(entries)
    if args.user:
        for_user = by_user_and_project.get(args.user)
        if not for_user:
            print(
                f"user {args.user} not found, found {' '.join(by_user_and_project.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)
        by_user_and_project = {args.user: for_user}
    if args.format == "humanreadable":
        print_humanreadable(by_user_and_project, args.currency)
    elif args.format == "csv":
        print_csv(by_user_and_project, args.currency)
    elif args.format == "json":
        print_json(by_user_and_project, args.currency)


if __name__ == "__main__":
    main()
