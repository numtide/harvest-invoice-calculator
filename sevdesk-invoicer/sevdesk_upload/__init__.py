#!/usr/bin/env python3

import argparse
import json
import mimetypes
import os
from datetime import datetime
from io import BufferedReader
from typing import Any
from urllib import parse, request

from sevdesk import Client
from sevdesk.client.api.voucher import create_voucher_by_factory, voucher_upload_file
from sevdesk.client.models.create_voucher_by_factory_json_body import (
    CreateVoucherByFactoryJsonBody,
)
from sevdesk.client.models.voucher_model import VoucherModel
from sevdesk.client.models.voucher_model_credit_debit import VoucherModelCreditDebit
from sevdesk.client.models.voucher_model_status import VoucherModelStatus
from sevdesk.client.models.voucher_model_supplier import VoucherModelSupplier
from sevdesk.client.models.voucher_model_voucher_type import VoucherModelVoucherType
from sevdesk.client.models.voucher_pos_model import VoucherPosModel
from sevdesk.client.models.voucher_pos_model_accounting_type import (
    VoucherPosModelAccountingType,
)
from sevdesk.client.models.voucher_upload_file_multipart_data import (
    VoucherUploadFileMultipartData,
)
from sevdesk.client.types import UNSET, File


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
        "--delete",
        action="store_true",
        help="Delete after upload",
    )
    parser.add_argument(
        "file", help="PDF/Image file to upload", type=argparse.FileType("rb"), nargs="+"
    )
    return parser.parse_args()


def create_voucher_from_pdf(
    client: Client,
    filename: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    headers = client.get_headers()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Accept"] = "application/json, text/plain, */*"
    url = "https://my.sevdesk.de/api/v1/Voucher/Factory/createFromPdf"
    data = parse.urlencode(
        dict(fileName=filename, mimeType="image/jpg", creditDebit="C")
    ).encode()
    req = request.Request(url, headers=headers, method="POST", data=data)
    resp = request.urlopen(req)
    json_resp = json.load(resp)
    return json_resp["objects"]["voucher"], json_resp["objects"]["positions"]


def val_or_unset(val: Any) -> Any:
    if val is None:
        return UNSET
    return val


def upload_file(file: BufferedReader, api_token: str) -> None:
    client = Client(base_url="https://my.sevdesk.de/api/v1", token=api_token)
    name = os.path.basename(file.name)
    f = File(payload=file, file_name=name, mime_type=mimetypes.guess_type(file.name)[0])
    res1 = voucher_upload_file.sync(
        client=client,
        multipart_data=VoucherUploadFileMultipartData(file=f),
    )
    voucher, positions = create_voucher_from_pdf(client, res1.objects.filename)
    supplier = UNSET
    if voucher.get("supplier"):
        supplier = VoucherModelSupplier(
            id=voucher["supplier"]["id"],
            object_name="Contact",
        )

    filename = res1.objects.filename
    sum_net = val_or_unset(voucher.get("sumNet"))
    sum_tax = val_or_unset("sumTax")
    sum_gross = val_or_unset(voucher.get("sumGross"))
    sum_net_accounting = val_or_unset(voucher.get("sumNetAccounting"))
    sum_gross_accounting = val_or_unset(voucher.get("sumGrossAccounting"))
    sum_discounts = val_or_unset(voucher.get("sumDiscounts"))
    sum_discounts_foreign_currency = val_or_unset(
        voucher.get("sumDiscountsForeignCurrency")
    )
    currency = val_or_unset(voucher.get("currency"))
    voucher_date = val_or_unset(voucher.get("voucherDate"))
    description = val_or_unset(voucher.get("description"))
    if voucher_date is not UNSET:
        voucher_date = datetime.fromisoformat(voucher_date)

    voucher = VoucherModel(
        object_name="Voucher",
        map_all=False,
        status=VoucherModelStatus.VALUE_50,
        tax_type="default",
        credit_debit=VoucherModelCreditDebit.C,
        supplier=supplier,
        voucher_type=VoucherModelVoucherType.VOU,
        sum_net=sum_net,
        sum_tax=sum_tax,
        sum_gross=sum_gross,
        sum_net_accounting=sum_net_accounting,
        sum_gross_accounting=sum_gross_accounting,
        sum_discounts=sum_discounts,
        sum_discounts_foreign_currency=sum_discounts_foreign_currency,
        currency=currency,
        description=description,
    )
    voucher_pos_save = []
    for pos in positions:
        t = pos["accountingType"]
        voucher_pos_save.append(
            VoucherPosModel(
                object_name="VoucherPos",
                map_all=False,
                voucher=UNSET,
                accounting_type=VoucherPosModelAccountingType(
                    id=t["id"], object_name=t["objectName"]
                ),
                tax_rate=pos["taxRate"],
                net=pos["net"],
                sum_net=pos["sumNet"],
                sum_gross=pos["sumGross"],
            )
        )

    factory = CreateVoucherByFactoryJsonBody(
        voucher=voucher,
        voucher_pos_save=voucher_pos_save,
        voucher_pos_delete=UNSET,
        filename=filename,
    )
    create_voucher_by_factory.sync(client=client, json_body=factory)


def main() -> None:
    args = parse_args()
    for file in args.file:
        upload_file(file, args.sevdesk_api_token)
        if args.delete:
            os.remove(file)


if __name__ == "__main__":
    main()
