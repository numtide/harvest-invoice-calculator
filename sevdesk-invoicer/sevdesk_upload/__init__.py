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
    # curl 'https://my.sevdesk.de/api/v1/Voucher/Factory/createFromPdf?cft=77cbb9eabfccd876c5acda36f22e6ebe' -X POST -H 'Accept: application/json, text/plain, */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Referer: https://my.sevdesk.de/' -H 'X-Frontend-Disable-Ui-Lock: true' -H 'Origin: https://my.sevdesk.de' -H 'DNT: 1' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' -H 'Connection: keep-alive' -H 'Cookie: sevToken=e5bc3a206eb5dcf4ebc329ad719d817b; sevInfo=p-b_sc-12_b-0_lang-de_m-0; intercom-session-q6owxyep=RFgvczlSUDkvYkMvazFZbnpsT1duQ3ovZ3FJRTdMejlpWnZqM3Y0N2Nzb0d2QSs1dlc1Y3pYeU03dDB0eUZNcy0tWmMydm5TZzhqa09tY0JUZ1BvK2RJZz09--404680691dfde842e4dfb8fe5af31fd81b047f08; intercom-device-id-q6owxyep=ed55f43c-4b50-4cd9-9022-cfb80f91bc2e' -H 'TE: trailers' --data-raw 'fileName=659cf4d74bac1ebbb613c0f1ba581c06.pdf&mimeType=image%2Fjpg&creditDebit=C'
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


# curl 'https://my.sevdesk.de/api/v1/Voucher/Factory/createFromPdf?cft=77cbb9eabfccd876c5acda36f22e6ebe' -X POST -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0' -H 'Accept: application/json, text/plain, */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Referer: https://my.sevdesk.de/' -H 'X-Frontend-Disable-Ui-Lock: true' -H 'Origin: https://my.sevdesk.de' -H 'DNT: 1' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' -H 'Connection: keep-alive' -H 'Cookie: sevToken=e5bc3a206eb5dcf4ebc329ad719d817b; sevInfo=p-b_sc-12_b-0_lang-de_m-0; intercom-session-q6owxyep=RFgvczlSUDkvYkMvazFZbnpsT1duQ3ovZ3FJRTdMejlpWnZqM3Y0N2Nzb0d2QSs1dlc1Y3pYeU03dDB0eUZNcy0tWmMydm5TZzhqa09tY0JUZ1BvK2RJZz09--404680691dfde842e4dfb8fe5af31fd81b047f08; intercom-device-id-q6owxyep=ed55f43c-4b50-4cd9-9022-cfb80f91bc2e' -H 'TE: trailers' --data-raw 'fileName=659cf4d74bac1ebbb613c0f1ba581c06.pdf&mimeType=image%2Fjpg&creditDebit=C'


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
    # curl 'https://my.sevdesk.de/api/v1/Voucher/Factory/saveVoucher?embed=accountingType,accountingType.accountingSystemNumber,supplier,object,additionalInfo,debit,acquisitionCostReference,propertyIsFirstVisit,accountDatev,propertyCateringTipForeignCurrency,propertyUseNewCalculation&cft=77cbb9eabfccd876c5acda36f22e6ebe' -X POST -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0' -H 'Accept: application/json, text/plain, */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Referer: https://my.sevdesk.de/' -H 'X-Version: default' -H 'Origin: https://my.sevdesk.de' -H 'DNT: 1' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' -H 'Connection: keep-alive' -H 'Cookie: sevToken=e5bc3a206eb5dcf4ebc329ad719d817b; sevInfo=p-b_sc-12_b-0_lang-de_m-0; intercom-session-q6owxyep=RFgvczlSUDkvYkMvazFZbnpsT1duQ3ovZ3FJRTdMejlpWnZqM3Y0N2Nzb0d2QSs1dlc1Y3pYeU03dDB0eUZNcy0tWmMydm5TZzhqa09tY0JUZ1BvK2RJZz09--404680691dfde842e4dfb8fe5af31fd81b047f08; intercom-device-id-q6owxyep=ed55f43c-4b50-4cd9-9022-cfb80f91bc2e' --data-raw 'voucher[create]=null&voucher[update]=null&voucher[sevClient]=null&voucher[voucherDate]=1688248800&voucher[supplier][id]=48509651&voucher[supplier][objectName]=Contact&voucher[estimatedContact]=null&voucher[supplierName]=null&voucher[description]=RG-2023-00254869&voucher[document]=null&voucher[resultDisdar]=%7B%22id%22%3A%22a9b77195-a4cd-437b-9bc6-1c919411c21a%22%2C%22confidence%22%3A0.0319820005001591%2C%22extractions%22%3A%5B%7B%22page%22%3A0%2C%22rawValue%22%3A%2211%2C19%22%2C%22parsedValue%22%3A1119%2C%22confidence%22%3A0.009151616011513397%2C%22label%22%3A%22AMOUNT%22%2C%22derived%22%3Afalse%7D%2C%7B%22page%22%3A0%2C%22rawValue%22%3A%22EUR%22%2C%22parsedValue%22%3A%22EUR%22%2C%22confidence%22%3A0.015669190945724647%2C%22label%22%3A%22CURRENCY%22%2C%22derived%22%3Afalse%7D%2C%7B%22page%22%3A0%2C%22rawValue%22%3A%2202.07.2023%22%2C%22parsedValue%22%3A%222023-07-02%22%2C%22confidence%22%3A0.07312456872314214%2C%22label%22%3A%22INVOICEDATE%22%2C%22derived%22%3Afalse%7D%2C%7B%22page%22%3A0%2C%22rawValue%22%3A%22RG-2023-00254869%22%2C%22parsedValue%22%3A%22RG-2023-00254869%22%2C%22confidence%22%3A0.032539485844154115%2C%22label%22%3A%22INVOICENUMBER%22%2C%22derived%22%3Afalse%7D%2C%7B%22page%22%3A0%2C%22rawValue%22%3A%2227%5C%2F050%5C%2F33841%22%2C%22parsedValue%22%3A%2227%5C%2F050%5C%2F33841%22%2C%22confidence%22%3A0.039295129012316465%2C%22label%22%3A%22TAXID%22%2C%22derived%22%3Afalse%7D%2C%7B%22page%22%3A0%2C%22rawValue%22%3A%2219%22%2C%22parsedValue%22%3A1900%2C%22confidence%22%3A0.032429403509013355%2C%22label%22%3A%22TAXRATE%22%2C%22derived%22%3Afalse%7D%2C%7B%22page%22%3A0%2C%22rawValue%22%3A%22DE308271755%22%2C%22parsedValue%22%3A%22DE308271755%22%2C%22confidence%22%3A0.021664609455249527%2C%22label%22%3A%22VATID%22%2C%22derived%22%3Afalse%7D%2C%7B%22page%22%3A0%2C%22rawValue%22%3A%229.40%22%2C%22parsedValue%22%3A940%2C%22confidence%22%3A0.2%2C%22label%22%3A%22NETAMOUNT%22%2C%22derived%22%3Atrue%7D%5D%2C%22positions%22%3A%5B%7B%22amount%22%3A1119%2C%22netAmount%22%3A940%2C%22taxRate%22%3A%2219%22%7D%5D%2C%22words%22%3A%5B%22(19%25)%22%2C%22(Penta%22%2C%22(non-EUR)%22%2C%22*Preispl%5Cu00e4ne%22%2C%22%2B49%22%2C%220%2C40%22%2C%2201.06.2023%22%2C%2202.07.2023%22%2C%221%25%22%2C%221%2C79%22%2C%2210245%22%2C%2211%2C19%22%2C%2211-13%22%2C%22180354%22%2C%22182607%22%2C%2223%22%2C%2227%5C%2F050%5C%2F33841%22%2C%2230%22%2C%2230.06.2023%22%2C%2230%5C%2F30*%22%2C%22311%22%2C%2240%2C00%22%2C%2285375%22%2C%229%2C00%22%2C%229%2C00%22%2C%229%2C40%22%2C%22983%22%2C%22Abwicklungsgeb%5Cu00fchr%22%2C%22Alexandre%22%2C%22Amtsgericht%22%2C%22Anregungen%22%2C%22Anzahl%22%2C%22Anzahl*%22%2C%22Bei%22%2C%22Berlin%22%2C%22Bezeichnung%22%2C%22Charlottenburg%22%2C%22DE308271755%22%2C%22Deutschland%22%2C%22Deutschland%22%2C%22Die%22%2C%22Diese%22%2C%22E-Mail%22%2C%22EUR%22%2C%22EUR%22%2C%22EUR%22%2C%22EUR%22%2C%22EUR%22%2C%22EUR%22%2C%22Einzelpreis%22%2C%22Fintech%22%2C%22Firmendaten%22%2C%22Fragen%22%2C%22Freising%22%2C%22Fremdw%5Cu00e4hrung%22%2C%22Gesamtpreis%22%2C%22Gesch%5Cu00e4ftsf%5Cu00fchrer%22%2C%22GmbH%22%2C%22Gr%5Cu00fc%5Cu00dfen%22%2C%22HRB%22%2C%22IT-Consulting%22%2C%22Ihr%22%2C%22J%5Cu00f6rg%22%2C%22Kartenzahlungen%22%2C%22Kontakt%22%2C%22Kunden-Nr.%3A%22%2C%22Leistungen%22%2C%22Leistungszeitraum%3A%22%2C%22Lukas%22%2C%22Mit%22%2C%22Neufahrn%22%2C%22PENTA%22%2C%22PENTA%22%2C%22PENTA%22%2C%22Penta%22%2C%22Penta%22%2C%22Plan%22%2C%22Platz%22%2C%22Pos.%22%2C%22Prot%22%2C%22Qonto%22%2C%22RG-2023-00254869%22%2C%22Rabe%22%2C%22Rechnung%22%2C%22Rechnung%22%2C%22Rechnung%22%2C%22Rechnung%22%2C%22Rechnungs-Nr.%3A%22%2C%22Rechnungsbetrag%22%2C%22Rechnungsdatum%3A%22%2C%22SE%22%2C%22Services).%22%2C%22Solaris%22%2C%22Starter%22%2C%22Steuernummer%3A%22%2C%22Tage%22%2C%22Team%22%2C%22Thalheim%22%2C%22Thomas-Mann-Stra%5Cu00dfe%22%2C%22Torben%22%2C%22Transaktionswerts%22%2C%22USt.-ID-Nr.%3A%22%2C%22Umsatzsteuer%22%2C%22Unterschrift%22%2C%22Unterst%5Cu00fctzt%22%2C%22Warschauer%22%2C%22Zwischensumme%22%2C%22Z%5Cu00f6rner%22%2C%22abgerechnet%22%2C%22an%22%2C%22bei%22%2C%22bitte%22%2C%22by%22%2C%22des%22%2C%22die%22%2C%22durch%22%2C%22durch%22%2C%22eine%22%2C%22elektronisch%22%2C%22enth%5Cu00e4lt%22%2C%22erbrachten%22%2C%22erstellt%22%2C%22freundlichen%22%2C%22f%5Cu00fcr%22%2C%22g%5Cu00fcltig.%22%2C%22help%40getpenta.com%22%2C%22https%3A%5C%2F%5C%2Fqonto.com%5C%2Fde%5C%2Fpenta%22%2C%22in%22%2C%22in%22%2C%22invoices%40getpenta.com.%22%2C%22ist%22%2C%22oder%22%2C%22ohne%22%2C%22schreibe%22%2C%22tagesgenau%22%2C%22und%22%2C%22uns%22%2C%22werden%22%2C%22wurde%22%2C%22zur%22%5D%7D&voucher[documentPreview]=null&voucher[payDate]=null&voucher[status]=50&voucher[object]=null&voucher[currency]=EUR&voucher[sumNet]=9.4&voucher[sumTax]=1.79&voucher[sumGross]=11.19&voucher[sumNetAccounting]=0&voucher[sumTaxAccounting]=0&voucher[sumGrossAccounting]=0&voucher[showNet]=1&voucher[paidAmount]=null&voucher[taxType]=default&voucher[creditDebit]=C&voucher[hidden]=null&voucher[costCentre]=null&voucher[origin]=null&voucher[voucherType]=VOU&voucher[recurringIntervall]=null&voucher[recurringInterval]=null&voucher[recurringStartDate]=null&voucher[recurringNextVoucher]=null&voucher[recurringLastVoucher]=null&voucher[recurringEndDate]=null&voucher[enshrined]=null&voucher[sendType]=null&voucher[inSource]=null&voucher[taxSet]=null&voucher[iban]=null&voucher[accountingSpecialCase]=null&voucher[paymentDeadline]=1689528905&voucher[tip]=0&voucher[mileageRate]=0&voucher[selectedForPaymentFile]=0&voucher[supplierNameAtSave]=PENTA&voucher[datevConnectOnline]=null&voucher[taxmaroStockAccount]=null&voucher[vatNumber]=DE308271755&voucher[deliveryDate]=1688248800&voucher[deliveryDateUntil]=null&voucher[sumDiscountNet]=0&voucher[sumDiscountGross]=0&voucher[sumNetForeignCurrency]=undefined&voucher[sumTaxForeignCurrency]=undefined&voucher[sumGrossForeignCurrency]=undefined&voucher[sumDiscountNetForeignCurrency]=0&voucher[sumDiscountGrossForeignCurrency]=0&voucher[taxRule]=null&voucher[objectName]=Voucher&voucher[types]=%5Bobject%20Object%5D&voucher[propertyIsFirstVisit]=true&voucher[tipForeign]=undefined&voucher[voucherDate_OCR]=1688248800&voucher[description_OCR]=RG-2023-00254869&voucher[vatNumber_OCR]=DE308271755&voucher[propertySupplierEstimatedBy]=disdarLookupTable&voucher[propertySupplierEstimatedContact]=48509651&voucher[accountingType]=null&voucher[mapAll]=true&voucher[total]=11.19&voucher[propertyForeignCurrencyDeadline]=1689528905&voucher[propertyExchangeRate]=null&voucher[propertyCreationOrigin]=edit_view&voucherPosSave[0][create]=null&voucherPosSave[0][update]=null&voucherPosSave[0][sevClient]=null&voucherPosSave[0][voucher]=null&voucherPosSave[0][accountingType][id]=74&voucherPosSave[0][accountingType][objectName]=AccountingType&voucherPosSave[0][estimatedAccountingType][id]=74&voucherPosSave[0][estimatedAccountingType][objectName]=AccountingType&voucherPosSave[0][taxRate]=19&voucherPosSave[0][sum]=9.399999999999999&voucherPosSave[0][net]=false&voucherPosSave[0][isAsset]=false&voucherPosSave[0][assetMemoValue]=null&voucherPosSave[0][sumNet]=9.399999999999999&voucherPosSave[0][sumTax]=0&voucherPosSave[0][sumGross]=11.19&voucherPosSave[0][sumNetAccounting]=0&voucherPosSave[0][sumTaxAccounting]=0&voucherPosSave[0][sumGrossAccounting]=0&voucherPosSave[0][comment]=null&voucherPosSave[0][isGwg]=false&voucherPosSave[0][cateringTaxRate]=null&voucherPosSave[0][cateringTip]=null&voucherPosSave[0][specialAccountingField1]=null&voucherPosSave[0][specialAccountingField2]=null&voucherPosSave[0][specialAccountingField3]=null&voucherPosSave[0][specialAccountingField4]=null&voucherPosSave[0][specialAccountingField5]=null&voucherPosSave[0][acquisitionCostReference]=null&voucherPosSave[0][accountDatev]=null&voucherPosSave[0][estimatedAccountDatev]=null&voucherPosSave[0][isPercentage]=null&voucherPosSave[0][discountedValue]=null&voucherPosSave[0][sumNetForeignCurrency]=0&voucherPosSave[0][sumTaxForeignCurrency]=0&voucherPosSave[0][sumGrossForeignCurrency]=0&voucherPosSave[0][sumDiscountForeignCurrency]=0&voucherPosSave[0][createNextPart]=0&voucherPosSave[0][objectName]=VoucherPos&voucherPosSave[0][types]=%5Bobject%20Object%5D&voucherPosSave[0][additionalInformation]=%7B%7D&voucherPosSave[0][taxRate_OCR]=19&voucherPosSave[0][vpAmount]=11.19&voucherPosSave[0][vpAmount_OCR]=11.19&voucherPosSave[0][propertyCateringTipForeignCurrency]=null&voucherPosSave[0][accountingType_tempEstimated][id]=74&voucherPosSave[0][accountingType_tempEstimated][objectName]=AccountingType&voucherPosSave[0][specialCaseTax]=false&voucherPosSave[0][taxRateDisabled]=false&voucherPosSave[0][accountingTypeSearchStr]=Kontof%C3%BChrung%20%2F%20Kartengeb%C3%BChren&voucherPosSave[0][mapAll]=true&voucherPosDelete=null&filename=71aebeb084c5fcc2acecc7225c773ffb.pdf&existenceCheck=true&forCashRegister=false'

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
