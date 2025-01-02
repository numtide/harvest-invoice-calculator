#!/usr/bin/env python3

# This script is currently only used by Jörg, in case someone else is also interested in using it,
# we can make it more flexible.
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

from sevdesk import Client
from sevdesk.accounting import Invoice, InvoiceStatus, LineItem, Unity
from sevdesk.client.api.contact import get_contacts
from sevdesk.client.models import DocumentModelTaxType
from sevdesk.common import SevDesk
from sevdesk.contact import Contact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    api_token = os.environ.get("SEVDESK_API_TOKEN")
    parser.add_argument(
        "--sevdesk-api-token",
        default=api_token,
        required=api_token is None,
        help="Get one from https://my.sevdesk.de/#/admin/userManagement",
    )
    parser.add_argument(
        "--customer",
        required=False,
        type=str,
        help="Ignore customer from json and assume this one instead",
    )
    parser.add_argument(
        "--payment-method",
        required=False,
        type=int,
        help="Payment method id to use for invoice. You can find the id by saving an existing method and see what the id is in the url in your network tab inspector.",
    )
    parser.add_argument(
        "--days-until-payment",
        required=False,
        type=int,
        default=30,
        help="Days until payment is due",
    )
    parser.add_argument(
        "json_file", help="JSON file containing reports (as opposed to stdin)"
    )
    return parser.parse_args()


def get_contact_by_name(client: Client, name: str) -> Contact:
    response = get_contacts.sync_detailed(client=client, name=name)
    SevDesk.raise_for_status(response, f"Failed to find customer with name {name}")
    assert response.parsed is not None
    contacts = response.parsed.objects
    assert isinstance(contacts, list)
    if len(contacts) == 0:
        msg = f"Could not find customer with name {name}. Please create it first in contacts."
        raise ValueError(msg)
    if len(contacts) > 1:
        ids = " ".join(c.customer_number for c in contacts)
        msg = f"Found multiple customers with name: {ids}"
        raise ValueError(msg)
    return Contact._from_contact_model(client, contacts[0])  # noqa: SLF001


def are_floats_similar(a: float, b: float, error_rate: float) -> bool:
    """Compare two floats to see if they are 'similar enough' within the specified error rate."""
    return abs(a - b) <= error_rate


def line_item(task: dict[str, Any], has_agency: bool) -> LineItem:
    price = float(
        round(
            (Fraction(task["target_cost"]) / Fraction(task["rounded_hours"])),
            2,
        )
    )
    if are_floats_similar(task["target_hourly_rate"], price, 0.01):
        price = task["target_hourly_rate"]
    else:
        msg = f"Price {price} is not similar to target hourly rate {task['target_hourly_rate']}"
        raise RuntimeError(msg)

    original_price = float(
        round(
            (Fraction(task["source_cost"]) / Fraction(task["rounded_hours"])),
            2,
        )
    )
    if are_floats_similar(task["source_hourly_rate"], original_price, 0.01):
        original_price = task["source_hourly_rate"]
    else:
        msg = f"Original price {original_price} is not similar to source hourly rate {task['source_hourly_rate']}"
        raise RuntimeError(msg)

    text = ""
    if task["source_currency"] != task["target_currency"]:
        text = f"{task['source_currency']} {original_price} x {float(task['exchange_rate'])} = {task['target_currency']} {price}"
    name = f"{task['client']} - {task['task']}" if has_agency else task["task"]
    return LineItem(
        name=name,
        unity=Unity.HOUR,
        tax=0,
        text=text,
        quantity=task["rounded_hours"],
        price=price,
    )


def create_invoice(
    api_token: str,
    customer_name: str | None,
    payment_method: str | None,
    tasks: list[dict[str, Any]],
    days_until_payment: int = 30,
) -> None:
    client = Client(base_url="https://my.sevdesk.de/api/v1", token=api_token)

    start = datetime.strptime(str(tasks[0]["start_date"]), "%Y%m%d")
    end = datetime.strptime(str(tasks[0]["end_date"]), "%Y%m%d")
    currency = tasks[0]["target_currency"]
    agency = tasks[0]["agency"]
    # agency == "-" is legacy
    has_agency = agency != "-" or agency != "none"
    if customer_name:
        billing_target = customer_name
    elif has_agency:
        billing_target = agency
    else:
        billing_target = tasks[0]["client"]
    items = [line_item(task, has_agency) for task in tasks]

    customer = get_contact_by_name(client, billing_target)

    head_text = f"""
    Terms of payment: Payment within {days_until_payment} days from receipt of invoice without deductions.
    """
    time = start.strftime("%Y-%m")
    invoice = Invoice(
        status=InvoiceStatus.DRAFT,
        header=f"Bill for {time}",
        head_text=head_text,
        customer=customer,
        reference=None,
        tax_type=DocumentModelTaxType.NOTEU,
        delivery_date=start,
        delivery_date_until=end,
        currency=currency,
        items=items,
    )
    if payment_method:
        invoice.payment_method = payment_method

    invoice.create(client)


def main() -> None:
    args = parse_args()
    if args.json_file:
        tasks = json.loads(Path(args.json_file).read_text())
    else:
        tasks = json.load(sys.stdin)
    create_invoice(
        args.sevdesk_api_token,
        args.customer,
        args.payment_method,
        tasks,
        args.days_until_payment,
    )


if __name__ == "__main__":
    main()
