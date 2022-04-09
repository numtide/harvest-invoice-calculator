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

* Generate using json output

```console
harvest-exporter --format json
```

* Generate using other currency

```console
harvest-exporter --currency CHF
```

## API References

* [Harvest](https://help.getharvest.com/api-v2)
* [Transferwise](https://api-docs.transferwise.com/#quotes-get-temporary-quote)
* [Sevdesk](https://my.sevdesk.de/api/InvoiceAPI/doc.html#tag/Invoice)
