import csv
import json
import sys
from fractions import Fraction

from . import User


def round_cents(n: Fraction) -> float:
    """
    Use this method only for displaying currencies to avoid rounding errors
    """
    return float(round(n, 2))


def as_humanreadable(
    users: dict[str, User],
    start_date: int,
    end_date: int,
    currency: str,
) -> None:
    print(f"time: {start_date} -> {end_date}")
    for user_name, user in users.items():
        print(f"{user_name}:")
        currencies = {}
        for client_name, client in user.clients.items():
            for task_name, task in client.tasks.items():
                if task.currency != currency:
                    currencies[task.currency] = task.exchange_rate(currency)
                round_cents(task.cost)
                converted_cost = round_cents(task.converted_cost(currency))
                converted_hourly_rate = round_cents(
                    task.converted_hourly_rate(currency)
                )

                print(
                    f"  {client_name} - {task_name} ({float(round(task.hourly_rate, 2))} {task.currency}/h -> {converted_hourly_rate} {currency}/h): {float(task.rounded_hours)}h -> {converted_cost} {currency}"
                )
        print("Exchange rates")
        for source_currency, rate in currencies.items():
            print(f"1 {source_currency} -> {float(rate)} {currency}")


def as_csv(
    users: dict[str, User],
    start_date: int,
    end_date: int,
    currency: str,
) -> None:
    fieldnames = [
        "user",
        "start_date",
        "end_date",
        "client",
        "task",
        "rounded_hours",
        "source_cost",
        "source_currency",
        "source_hourly_rate",
        "target_cost",
        "target_currency",
        "target_hourly_rate",
        "exchange_rate",
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    for user_name, user in users.items():
        for client_name, client in user.clients.items():
            for task_name, project in client.tasks.items():
                writer.writerow(
                    dict(
                        user=user_name,
                        start_date=start_date,
                        end_date=end_date,
                        client=client_name,
                        task=task_name,
                        rounded_hours=float(project.rounded_hours),
                        source_hourly_rate=round_cents(project.hourly_rate),
                        source_cost=round_cents(project.cost),
                        source_currency=project.currency,
                        target_hourly_rate=round_cents(
                            project.converted_hourly_rate(currency)
                        ),
                        target_cost=round_cents(project.converted_cost(currency)),
                        target_currency=currency,
                        exchange_rate=float(project.exchange_rate(currency)),
                    )
                )


def as_json(
    users: dict[str, User],
    start_date: int,
    end_date: int,
    currency: str,
) -> None:
    data = []
    for user_name, user in users.items():
        for client_name, client in user.clients.items():
            for task_name, project in client.tasks.items():
                data.append(
                    dict(
                        user=user_name,
                        start_date=start_date,
                        end_date=end_date,
                        client=client_name,
                        task=task_name,
                        rounded_hours=float(project.rounded_hours),
                        source_hourly_rate=round_cents(project.hourly_rate),
                        source_cost=round_cents(project.cost),
                        source_currency=project.currency,
                        target_hourly_rate=round_cents(
                            project.converted_hourly_rate(currency)
                        ),
                        target_cost=round_cents(project.converted_cost(currency)),
                        target_currency=currency,
                        exchange_rate=float(project.exchange_rate(currency)),
                    )
                )
    json.dump(data, sys.stdout, indent=4, sort_keys=True)
