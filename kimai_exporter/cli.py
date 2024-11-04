#!/usr/bin/env python3

import argparse
import calendar
import os
import sys
from datetime import date, datetime, timedelta
from fractions import Fraction

import kimai

from . import Task, aggregate_time_entries, export


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    token = os.environ.get("KIMAI_API_KEY")
    parser.add_argument(
        "--kimai-api-key",
        default=os.environ.get("KIMAI_API_KEY"),
        required=token is None,
        help="Get one from your kimai account (env: KIMAI_API_KEY)",
    )
    parser.add_argument(
        "--hourly-rate",
        type=Fraction,
        help="Use this hourly rate instead of the one from kimai",
    )
    user = os.environ.get("KIMAI_USER")
    parser.add_argument(
        "--user",
        type=str,
        default=user,
        required=user is None,
        help="user to filter for (env: KIMAI_USER)",
    )
    parser.add_argument(
        "--start",
        type=lambda s: datetime.strptime(s + "T00:00:00", "%Y-%m-%dT%H:%M:%S"),
        help="Start date i.e. YYYY-MM-DD",
    )
    parser.add_argument(
        "--end",
        type=lambda s: datetime.strptime(s + "T00:00:00", "%Y-%m-%dT%H:%M:%S"),
        help="End date i.e. YYYY-MM-DD",
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
        "--client",
        type=str,
        required=True,
        help="Export report for this client only",
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
        choices=("humanreadable", "csv", "json", "table"),
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


def exclude_task(task: Task, args: argparse.Namespace) -> bool:
    if args.client == task.client:
        # allow to export external projects if --client is passed and matches
        return False
    if args.client:
        return True

    return task.is_external


NUMTIDE_RATE = Fraction(0.75)


def main() -> None:
    args = parse_args()

    projects = kimai.get_visible_projects(args.kimai_api_key)
    projects = list(filter(lambda x: x["parentTitle"] == args.client, projects))
    if len(projects) < 1:
        msg = f"Projects for client {args.client} not found"
        raise Exception(msg)

    users = kimai.get_visible_users(args.kimai_api_key)
    users = list(
        filter(lambda x: x["username"] == args.user or x["alias"] == args.user, users)
    )
    if len(users) < 1:
        raise Exception(f"User {args.user} not found")
    if len(users) > 1:
        raise Exception(f"Multiple users found for {args.user}")
    user = users[0]

    timesheets = {}
    for project in projects:
        entries = kimai.get_time_entries(
            args.kimai_api_key, args.start, args.end, user["id"], project["id"]
        )
        timesheets[project["name"]] = entries

    time_per_project = {}
    for project, entries in timesheets.items():
        total_seconds = sum(entry["duration"] for entry in entries)
        hours = total_seconds / 3600
        time_per_project[project] = {"hours": hours}

    breakpoint()
    agency_rate = None
    if args.agency == "numtide":
        agency_rate = NUMTIDE_RATE

    users = aggregate_time_entries(entries, args.hourly_rate, agency_rate)

    if args.user:
        for_user = users.get(args.user)
        if not for_user:
            print(
                f"user {args.user} not found in time range, found {', '.join(users.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)
        users = {args.user: for_user}

    for _, user in users.items():
        for _, client in user.clients.items():
            to_delete = []
            for name, task in client.tasks.items():
                if exclude_task(task, args):
                    to_delete.append(name)
            for name in to_delete:
                del client.tasks[name]

    fn = None
    if args.format == "humanreadable":
        fn = export.as_humanreadable
    elif args.format == "csv":
        fn = export.as_csv
    elif args.format == "table":
        fn = export.as_rich_table
    else:  # args.format == "json":
        fn = export.as_json
    fn(users, args.start, args.end, args.currency)


if __name__ == "__main__":
    main()
