#!/usr/bin/env python3

# This script is currently only used by Jörg, in case someone else is also interested in using it,
# we can make it more flexible.

import argparse
import datetime
import json
import os
import pprint
import sys
from pathlib import Path
from typing import Any, NoReturn

from sevdesk import Client
from sevdesk.client.api.check_account import create_check_account, get_check_accounts
from sevdesk.client.api.check_account_transaction import create_transaction
from sevdesk.client.models.check_account_model import (
    CheckAccountModel,
    CheckAccountModelImportType,
    CheckAccountModelStatus,
    CheckAccountModelType,
)
from sevdesk.client.models.check_account_transaction_model import (
    CheckAccountTransactionModel,
)
from sevdesk.client.models.check_account_transaction_model_check_account import (
    CheckAccountTransactionModelCheckAccount,
)
from sevdesk.client.models.check_account_transaction_model_status import (
    CheckAccountTransactionModelStatus,
)
from sevdesk.client.types import UNSET, Unset


def die(msg: str) -> NoReturn:
    print(msg, file=sys.stderr)
    sys.exit(1)


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
        "--import-state-file",
        default="import-state.json",
        help="Used to memorize already imported transactions",
    )
    parser.add_argument(
        "json_file",
        help="JSON file containing wise bank statements (as opposed to stdin)",
    )
    return parser.parse_args()


def get_or_create_account(client: Client, name: str, currency: str) -> int:
    res = get_check_accounts.sync(client=client)
    if res is not None and res.objects is not Unset:
        for obj in res.objects:
            if obj.name == name:
                return obj.id
    account = CheckAccountModel(
        name=name,
        type=CheckAccountModelType.ONLINE,
        currency=currency,
        status=CheckAccountModelStatus.VALUE_100,
        id=UNSET,
        object_name=UNSET,
        create=UNSET,
        update=UNSET,
        sev_client=UNSET,
        import_type=CheckAccountModelImportType.CSV,
        bank_server=UNSET,
        auto_map_transactions=1,
    )

    res = create_check_account.sync(client=client, json_body=account)
    if res is None or res.objects is Unset:
        die(f"Failed to create account {name}")
    return res.objects.id


def import_statements(
    api_token: str, statements: dict[str, Any], import_state_file: Path
) -> None:
    client = Client(base_url="https://my.sevdesk.de/api/v1", token=api_token)
    # Attributes:
    #     name (str): Name of the check account Example: Iron Bank.
    #     type (CheckAccountModelType): The type of the check account. Account with a CSV or MT940 import are regarded as
    #         online.<br>
    #              Apart from that, created check accounts over the API need to be offline, as online accounts with an active
    #         connection
    #              to a bank application can not be managed over the API. Example: online.
    #     currency (str): The currency of the check account. Example: EUR.
    #     status (CheckAccountModelStatus): Status of the check account. 0 <-> Archived - 100 <-> Active Default:
    #         CheckAccountModelStatus.VALUE_100.
    #     id (Union[Unset, int]): The check account id
    #     object_name (Union[Unset, str]): The check account object name
    #     create (Union[Unset, datetime.datetime]): Date of check account creation
    #     update (Union[Unset, datetime.datetime]): Date of last check account update
    #     sev_client (Union[Unset, CheckAccountModelSevClient]): Client to which check account belongs. Will be filled
    #         automatically
    #     import_type (Union[Unset, None, CheckAccountModelImportType]): Import type. Transactions can be imported by this
    #         method on the check account. Example: CSV.
    #     default_account (Union[Unset, CheckAccountModelDefaultAccount]): Defines if this check account is the default
    #         account. Default: CheckAccountModelDefaultAccount.VALUE_0.
    #     bank_server (Union[Unset, str]): Bank server of check account
    #     auto_map_transactions (Union[Unset, None, int]): Defines if transactions on this account are automatically
    #         mapped to invoice and vouchers when imported if possible. Default: 1.
    currency = statements["query"]["currency"]

    bank = statements["bankDetails"][0]
    if len(bank["accountNumbers"]) != 1:
        die(
            f"Expected exactly one account number in bank statement found: {statements['bankDetails']['accountNumbers']}"
        )
    account_id = bank["accountNumbers"][0]["accountNumber"]
    currency = statements["query"]["currency"]
    name = f"Wise ({currency}, {account_id})"
    account_id = get_or_create_account(client, name, currency)
    datetime.datetime.strptime(
        statements["query"]["intervalStart"], "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=datetime.timezone.utc)
    datetime.datetime.strptime(
        statements["query"]["intervalEnd"], "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=datetime.timezone.utc)

    if import_state_file.exists():
        imported_transactions = set(json.loads(import_state_file.read_text()))
    else:
        imported_transactions = set()
    for wise_transaction in statements["transactions"]:
        transaction_id = (
            f"{currency}-{account_id}-{wise_transaction['referenceNumber']}"
        )
        if transaction_id in imported_transactions:
            print(f"Skipping already imported transaction {transaction_id}")
            continue
        # value_date (datetime.datetime): Date the check account transaction was booked Example: 01.01.2022.
        # amount (float): Amount of the transaction Example: 100.
        # payee_payer_name (str): Name of the payee/payer Example: Cercei Lannister.
        # check_account (CheckAccountTransactionModelCheckAccount): The check account to which the transaction belongs
        # status (CheckAccountTransactionModelStatus): Status of the check account transaction.<br>
        #         100 <-> Created<br>
        #         200 <-> Linked<br>
        #         300 <-> Private<br>
        #         400 <-> Booked
        # id (Union[Unset, int]): The check account transaction id
        # object_name (Union[Unset, str]): The check account transaction object name
        # create (Union[Unset, datetime.datetime]): Date of check account transaction creation
        # update (Union[Unset, datetime.datetime]): Date of last check account transaction update
        # sev_client (Union[Unset, CheckAccountTransactionModelSevClient]): Client to which check account transaction
        #    belongs. Will be filled automatically
        # entry_date (Union[Unset, datetime.datetime]): Date the check account transaction was imported Example:
        #    01.01.2022.
        # paymt_purpose (Union[Unset, str]): the purpose of the transaction Example: salary.
        # enshrined (Union[Unset, None, datetime.datetime]): Defines if the transaction has been enshrined and can not be
        #    changed any more.
        # source_transaction (Union[Unset, None, CheckAccountTransactionModelSourceTransaction]): The check account
        #    transaction serving as the source of the rebooking
        # target_transaction (Union[Unset, None, CheckAccountTransactionModelTargetTransaction]): The check account
        #    transaction serving as the target of the rebooking

        t = wise_transaction["details"]["type"]
        if wise_transaction["type"] == "CREDIT":
            if t == "MONEY_ADDED":
                payee_payer_name = wise_transaction["details"]["description"]
            else:
                payee_payer_name = wise_transaction["details"]["senderName"]
        else:
            t = wise_transaction["details"]["type"]
            if t == "DIRECT_DEBIT":
                payee_payer_name = wise_transaction["details"]["originator"]
            elif t == "TRANSFER":
                payee_payer_name = wise_transaction["details"]["recipient"]["name"]
            elif t == "UNKNOWN":  # seen only for initial account purchase so far
                payee_payer_name = "Wise"
            else:
                pprint.pprint(wise_transaction)
                die(f"Unknown transaction type {t} in transaction above")

        paymt_purpose = wise_transaction["details"].get(
            "paymentReference", wise_transaction["details"]["description"]
        )
        date = datetime.datetime.strptime(
            wise_transaction["date"], "%Y-%m-%dT%H:%M:%S.%fZ"
        ).replace(tzinfo=datetime.timezone.utc)
        transaction = CheckAccountTransactionModel(
            check_account=CheckAccountTransactionModelCheckAccount(
                id=account_id, object_name="CheckAccount"
            ),
            status=CheckAccountTransactionModelStatus.VALUE_100,
            value_date=date,
            entry_date=date,
            amount=wise_transaction["amount"]["value"],
            payee_payer_name=payee_payer_name,
            paymt_purpose=paymt_purpose,
        )
        create_transaction.sync(client=client, json_body=transaction)
        imported_transactions.add(transaction_id)
        import_state_file.write_text(json.dumps(list(imported_transactions)))


def main() -> None:
    args = parse_args()
    if args.json_file:
        with open(args.json_file) as f:
            statements_per_account = json.load(f)
    else:
        statements_per_account = json.load(sys.stdin)

    for statements in statements_per_account:
        import_statements(
            args.sevdesk_api_token, statements, Path(args.import_state_file)
        )


if __name__ == "__main__":
    main()
