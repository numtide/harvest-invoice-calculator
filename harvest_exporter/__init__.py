#!/usr/bin/env python3

import re
import sys
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Optional

from .transferwise import exchange_rate

NUMTIDE_RATE = 0.75


def convert_currency(
    amount: Fraction, source_currency: str, target_currency: str
) -> Fraction:
    rate = exchange_rate(source_currency, target_currency)
    return amount * rate


@dataclass
class Project:
    # Use fractions here to avoid rounding errors, round to cents once on export
    rounded_hours: Fraction = Fraction(0)
    cost: Fraction = Fraction(0)
    hourly_rate: Fraction = Fraction(0)
    currency: str = ""
    country_code: str = ""

    def exchange_rate(self, currency: str) -> Fraction:
        return exchange_rate(self.currency, currency)

    def converted_cost(self, currency: str) -> Fraction:
        return convert_currency(self.cost, self.currency, currency)

    def converted_hourly_rate(self, currency: str) -> Fraction:
        return convert_currency(self.hourly_rate, self.currency, currency)


Aggregated = Dict[str, Dict[str, Project]]


def aggregate_time_entries(
    entries: List[Dict[str, Any]], hourly_rate: Optional[Fraction]
) -> Aggregated:
    by_user_and_project: Dict[str, Dict[str, Project]] = defaultdict(
        lambda: defaultdict(lambda: Project())
    )
    for entry in entries:
        client_name = entry["client"]["name"]
        task_name = entry["task"]["name"]
        actual_project_name = entry["project"]["name"]
        # Parse the numtide country code from the project name
        m = re.match(r".+ - (UK|CH)$", actual_project_name)

        if m is None:
            print(
                f"WARNING, project name {actual_project_name} does not contain a country code. Assuming UK",
                file=sys.stderr,
            )
            country_code = "UK"
        else:
            country_code = m.group(1)

        project_name = f"{client_name} - {task_name}"
        if hourly_rate is not None:
            rate = hourly_rate
        else:
            rate = entry["task_assignment"]["hourly_rate"]
            if rate == 0 or rate is None:
                print(
                    f"WARNING, hourly rate for {client_name}{task_name}/{entry['task']['name']} is 0.0, skip for export",
                    file=sys.stderr,
                )
                continue

        project = by_user_and_project[entry["user"]["name"]][project_name]
        # the developer's hourly rate is what we charge to the customer, minus 25%
        project.hourly_rate = rate * Fraction(NUMTIDE_RATE)
        rounded_hours = Fraction(entry["rounded_hours"])
        project.rounded_hours += rounded_hours
        if project.country_code == "":
            project.country_code = country_code
        else:
            msg = f"Country code of customer changed from {project.country_code} to {country_code} within the billing period. This is not supported!"
            assert project.country_code == country_code, msg

        if project.currency == "":
            project.currency = entry["client"]["currency"]
        else:
            msg = f"Currency of customer changed from {project.currency} to {entry['client']['currency']} within the billing period. This is not supported!"
            assert project.currency == entry["client"]["currency"], msg
        project.cost += rounded_hours * Fraction(project.hourly_rate)

    for user, projects in by_user_and_project.items():
        by_user_and_project[user] = OrderedDict(sorted(projects.items()))
    return OrderedDict(sorted(by_user_and_project.items()))
