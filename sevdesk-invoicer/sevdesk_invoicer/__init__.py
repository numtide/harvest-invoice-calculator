#!/usr/bin/env python3

# This script is currently only used by Jörg, in case someone else is also interested in using it,
# we can make it more flexible.

import argparse
import os
import sys
import json
from fractions import Fraction
from datetime import datetime
from typing import Dict, Any, List

from sevdesk import Client
from sevdesk.contact import Customer
from sevdesk.client.models import Invoice, DocumentModelTaxType
from sevdesk.accounting import (
    Invoice,
    InvoiceStatus,
    LineItem,
    Unity,
)


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
        "json_file", help="JSON file containing reports (as opposed to stdin)"
    )
    return parser.parse_args()


def create_invoice(api_token: str, projects: List[Dict[str, Any]]) -> None:
    client = Client(base_url="https://my.sevdesk.de/api/v1", token=api_token)
    customer = Customer.get_by_customer_number(client, "1000")
    items = []
    for project in projects:
        price = float(
            round(
                (Fraction(project["target_cost"]) / Fraction(project["rounded_hours"])),
                2,
            )
        )
        original_price = float(
            round(
                (Fraction(project["source_cost"]) / Fraction(project["rounded_hours"])),
                2,
            )
        )
        if project['source_currency'] != project['target_currency']:
            text = f"{project['source_currency']} {original_price} x 0.8 x {float(project['exchange_rate'])} = {project['target_currency']} {price}"
        else:
            text = f"{project['source_currency']} {original_price} x 0.8 = {project['source_currency']} {price}"
        items.append(
            LineItem(
                name=project["project"],
                unity=Unity.HOUR,
                tax=0,
                text=text,
                quantity=project["rounded_hours"],
                price=price,
            )
        )
    start = datetime.strptime(projects[0]["start_date"], "%Y%m%d")
    end = datetime.strptime(projects[0]["end_date"], "%Y%m%d")

    head_text = """
    Terms of payment: Payment within 30 days from receipt of invoice without deductions.
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
        items=items,
    )
    invoice.create(client)
    pass


def main() -> None:
    args = parse_args()
    if args.json_file:
        with open(args.json_file) as f:
            projects = json.load(f)
    else:
        projects = json.load(sys.stdin)
    create_invoice(args.sevdesk_api_token, projects)


if __name__ == "__main__":
    main()
