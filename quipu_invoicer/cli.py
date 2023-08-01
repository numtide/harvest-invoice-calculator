import argparse
import json
import os

from api import QuipuAPI


def pprint(data):
    print(json.dumps(data, indent=4))


def invoice_data_type(arg):
    return json.load(argparse.FileType("r")(arg))


def create_parser():
    quipu_app_id = os.environ.get("QUIPU_APP_ID")
    quipu_api_secret = os.environ.get("QUIPU_APP_SECRET")

    parser = argparse.ArgumentParser(description="Interact with Quipu API.")
    parser.add_argument(
        "--quipu-app-id",
        default=quipu_app_id,
        required=quipu_app_id is None,
        help="Application ID for Quipu API. Get one from https://getquipu.com/d/aldoborrero/integrations",
    )
    parser.add_argument(
        "--quipu-app-secret",
        default=quipu_api_secret,
        required=quipu_api_secret is None,
        help="Application Secret for Quipu API. Get one from https://getquipu.com/d/aldoborrero/integrations",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list_invoices", help="List all invoices.")
    parser_get_invoice = subparsers.add_parser(
        "get_invoice", help="Get a specific invoice."
    )
    parser_get_invoice.add_argument("invoice_id", help="ID of the invoice.")

    parser_create_ivnoice = subparsers.add_parser(
        "create_invoice", help="Create a new invoice."
    )
    parser_create_ivnoice.add_argument(
        "invoice_data", type=invoice_data_type, help="Invoice data as a JSON file."
    )

    parser_update_invoice = subparsers.add_parser(
        "update_invoice", help="Update an existing invoice."
    )
    parser_update_invoice.add_argument("invoice_id", help="ID of the invoice.")
    parser_update_invoice.add_argument(
        "invoice_data", type=invoice_data_type, help="Invoice data as a JSON file."
    )

    subparsers.add_parser("list_contacts", help="List all contacts.")

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    quipu_api = QuipuAPI(args.quipu_app_id, args.quipu_app_secret)

    command_to_function = {
        "list_invoices": (quipu_api.list_invoices, ()),
        "get_invoice": (quipu_api.get_invoice, ("invoice_id",)),
        "create_invoice": (quipu_api.create_invoice, ("invoice_data",)),
        "update_invoice": (quipu_api.update_invoice, ("invoice_id", "invoice_data")),
        "list_contacts": (quipu_api.list_contacts, ()),
    }

    func, arg_names = command_to_function.get(args.command)
    args_dict = vars(args)
    args_for_func = {name: args_dict[name] for name in arg_names if args_dict.get(name)}

    if func and callable(func):
        pprint(func(**args_for_func))


if __name__ == "__main__":
    main()
