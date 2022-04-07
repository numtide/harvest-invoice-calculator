from fractions import Fraction
import sys
import csv
import json

from . import Aggregated


def round_cents(n: Fraction) -> float:
    """
    Use this method only for displaying currencies to avoid rounding errors
    """
    return float(round(n, 2))


def as_humanreadable(
    by_user_and_project: Aggregated, start_date: int, end_date: int, currency: str
) -> None:
    print(f"time: {start_date} -> {end_date}")
    for user, projects in by_user_and_project.items():
        print(f"{user}:")
        currencies = {}
        for project_name, project in projects.items():
            if project.currency != currency:
                currencies[project.currency] = project.exchange_rate(currency)
            cost = round_cents(project.cost)
            converted_cost = round_cents(project.converted_cost(currency))

            print(
                f"  {project_name}: {float(project.rounded_hours)}h, {cost} {project.currency} -> {converted_cost} {currency}"
            )
        print("Exchange rates")
        for source_currency, rate in currencies.items():
            print(f"1 {source_currency} -> {float(rate)} {currency}")


def as_csv(
    by_user_and_project: Aggregated, start_date: int, end_date: int, currency: str
) -> None:
    fieldnames = [
        "user",
        "start_date",
        "end_date",
        "project",
        "rounded_hours",
        "source_cost",
        "source_currency",
        "target_cost",
        "target_currency",
        "exchange_rate"
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for user, projects in by_user_and_project.items():
        for project_name, project in projects.items():
            writer.writerow(
                dict(
                    user=user,
                    start_date=start_date,
                    end_date=end_date,
                    project=project_name,
                    rounded_hours=float(project.rounded_hours),
                    source_cost=round_cents(project.cost),
                    source_currency=project.currency,
                    target_cost=round_cents(project.converted_cost(currency)),
                    target_currency=currency,
                    exchange_rate=float(project.exchange_rate(currency))
                )
            )


def as_json(
    by_user_and_project: Aggregated, start_date: int, end_date: int, currency: str
) -> None:
    data = []
    for user, projects in by_user_and_project.items():
        for project_name, project in projects.items():
            data.append(
                dict(
                    user=user,
                    start_date=start_date,
                    end_date=end_date,
                    project=project_name,
                    rounded_hours=float(project.rounded_hours),
                    source_cost=round_cents(project.cost),
                    source_currency=project.currency,
                    target_cost=round_cents(project.converted_cost(currency)),
                    target_currency=currency,
                    exchange_rate=float(project.exchange_rate(currency))
                )
            )
    json.dump(data, sys.stdout, indent=4, sort_keys=True)
