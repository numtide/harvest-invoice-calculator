#!/usr/bin/env python3

import argparse
import calendar
import os
import sys
from datetime import date, datetime, timedelta

from harvest import get_time_entries

from . import aggregate_time_entries, export


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    account = os.environ.get("HARVEST_ACCOUNT_ID")
    parser.add_argument(
        "--harvest-account-id",
        default=account,
        required=account is None,
        help="Get one from https://id.getharvest.com/developers (env: HARVEST_ACCOUNT_ID)",
    )
    token = os.environ.get("HARVEST_BEARER_TOKEN")
    parser.add_argument(
        "--harvest-bearer-token",
        default=os.environ.get("HARVEST_BEARER_TOKEN"),
        required=token is None,
        help="Get one from https://id.getharvest.com/developers (env: HARVEST_BEARER_TOKEN)",
    )
    parser.add_argument(
        "--user",
        type=str,
        default=os.environ.get("HARVEST_USER"),
        help="user to filter for (env: HARVEST_USER)",
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
        "--year",
        type=int,
        help="Year to generate report for (conflicts with `--start` and `--end`)",
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
        year = today.year
        if args.year:
            year = args.year
        _, last_day = calendar.monthrange(year, args.month)
        args.start = date(year, args.month, 1).strftime("%Y%m%d")
        args.end = date(year, args.month, last_day).strftime("%Y%m%d")
    elif (args.start and not args.end) or (args.end and not args.start):
        print("both --start and --end flag must be passed", file=sys.stderr)
        sys.exit(1)
    elif not args.start and not args.end:
        # Show the previous month by default
        start_of_month = today.replace(day=1)
        end_of_previous_month = start_of_month - timedelta(days=1)
        args.start = end_of_previous_month.strftime("%Y%m01")
        args.end = end_of_previous_month.strftime("%Y%m%d")

    return args


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
                f"user {args.user} not found in time range, found {', '.join(by_user_and_project.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)
        by_user_and_project = {args.user: for_user}
    fn = None
    if args.format == "humanreadable":
        fn = export.as_humanreadable
    elif args.format == "csv":
        fn = export.as_csv
    else:  # args.format == "json":
        fn = export.as_json
    fn(by_user_and_project, args.start, args.end, args.currency)


if __name__ == "__main__":
    main()
