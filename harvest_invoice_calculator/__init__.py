#!/usr/bin/env python3

from collections import defaultdict
import os
import sys
import calendar
from typing import Dict, Any, List
from fractions import Fraction
from dataclasses import dataclass

from .transferwise import exchange_rate

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
