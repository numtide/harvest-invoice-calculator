# Harvest invoice calculator

Create your invoice based on [Harvest](https://numtide.harvestapp.com) timesheets
and calculate the exchange rate to your currency using [Transferwise](https://transferwise.com).

Optional: generate invoice using Sevdesk

## Requirements

Generate your personal access token in Harvest using [this page](https://id.getharvest.com/oauth2/access_tokens/new).

```console
cp .envrc.local-template .envrc.local
```

Save your Account ID and your token in `.envrc.local`

## Usage / Examples

* Generate for the current month

```console
harvest-exporter
```

* Generate for march:

```console
harvest-exporter --month 3
```

* Filter by user

```console
harvest-exporter --user "Jörg Thalheim"
```

* Filter by country (UK/CH)

``` console
harvest-exporter --country UK
harvest-exporter --country CH
```

* Generate using json output

```console
harvest-exporter --format json
```

* Generate using other currency

```console
harvest-exporter --currency CHF
```

* Override hourly rate:

```
harvest-exporter  --hourly-rate 100
```

This will override the hourly rate reported by harvest prior to applying the nutmide rate.

* Filter by client:

```
harvest-exporter --client "Kuutamo"
```

This can be also used to export hours for clients that are external to numtide (client name starting with "External -")

* Generate an invoice with [sevdesk](https://sevdesk.de)

Generate a bill from the harvest exprt for the customer with the ID 1000

```
$ sevdesk-invoicer --customer "1000" harvest.json
```

* Calculate working days from harvest time report.

  For income tax in Germany one can claim money back for each day. The time report can be obtained from [here](https://numtide.harvestapp.com/reports) for each user.
  Than run this script:


``` console
$ working-days-calculator report.csv
Working days: 171 from 2022-01-12 00:00:00 to 2022-12-29 00:00:00
```



## API References

* [Harvest](https://help.getharvest.com/api-v2)
* [Transferwise](https://api-docs.transferwise.com/#quotes-get-temporary-quote)
* [Sevdesk](https://my.sevdesk.de/api/InvoiceAPI/doc.html#tag/Invoice)
