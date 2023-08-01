# import argparse
# import json
# import os
# import sys
# from typing import Any, Dict, List

# from .api import QuipuAPI

# # This script is currently only used by Aldo Borrero, in case someone else is also interested in using it,
# # we can make it more flexible.


# def parse_args() -> argparse.Namespace:
#     quipu_app_id = os.environ.get("QUIPU_APP_ID")
#     quipu_api_secret = os.environ.get("QUIPU_APP_SECRET")

#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "--quipu-app-id",
#         default=quipu_app_id,
#         required=quipu_app_id is None,
#         help="Get one from https://getquipu.com/d/aldoborrero/integrations",
#     )
#     parser.add_argument(
#         "--quipu-app-secret",
#         default=quipu_api_secret,
#         required=quipu_api_secret is None,
#         help="Get one from https://getquipu.com/d/aldoborrero/integrations",
#     )
#     parser.add_argument(
#         "--customer",
#         required=False,
#         type=str,
#         help="Ignore customer from json and assume this one instead",
#     )
#     parser.add_argument(
#         "--payment-method",
#         required=False,
#         type=int,
#         help="Payment method id to use for invoice. You can find the id by saving an existing method and see what the id is in the url in your network tab inspector.",
#     )
#     parser.add_argument(
#         "json_file", help="JSON file containing reports (as opposed to stdin)"
#     )
#     return parser.parse_args()


# def create_invoice(
#     app_id: str,
#     app_secret: str,
#     tasks: List[Dict[str, Any]],
# ) -> None:
#     quipu_api = QuipuAPI(
#         app_id=app_id,
#         app_secret=app_secret,
#     )

#     invoice_data = """
#         {
#             "data": {
#                 "type": "invoices",
#                 "attributes": {
#                     "kind": "income",
#                     "number": null,
#                     "issue_date": "2023-08-01",
#                     "due_date": "2023-08-15",
#                     "paid_at": null,
#                     "payment_method": "bank_transfer",
#                     "tags": "songo, timba"
#                 },
#                 "relationships": {
#                     "contact": {
#                         "data": {
#                             "id": 6347,
#                             "type": "contacts"
#                         }
#                     },
#                     "accounting_category": {
#                         "data": {
#                             "id": 123,
#                             "type": "accounting_categories"
#                         }
#                     },
#                     "items": {
#                         "data": [
#                             {
#                                 "type": "book_entry_items",
#                                 "attributes": {
#                                     "concept": "Tornillos",
#                                     "unitary_amount": "0.50",
#                                     "quantity": 30,
#                                     "vat_percent": 21,
#                                     "retention_percent": 0
#                                 }
#                             }
#                         ]
#                     }
#                 }
#             }
#         }
#     """

#     quipu_api.create_invoice(invoice_data)

#     # print(json.dumps(invoice, indent=4))


# def main() -> None:
#     args = parse_args()

#     if args.json_file:
#         with open(args.json_file) as f:
#             tasks = json.load(f)
#     else:
#         tasks = json.load(sys.stdin)

#     create_invoice(
#         args.quipu_app_id,
#         args.quipu_app_secret,
#         tasks,
#     )


# if __name__ == "__main__":
#     main()
