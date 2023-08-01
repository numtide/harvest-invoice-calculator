import base64

import requests


class QuipuAPI:
    def __init__(self, app_id, app_secret):
        self._base_url = "https://getquipu.com/"
        self._app_id = app_id
        self._app_secret = app_secret
        self._token = None
        self._headers = {
            "Accept": "application/vnd.quipu.v1+json",
            "Content-Type": "application/vnd.quipu.v1+json",
        }
        self.get_token()

    def _generate_auth_header(self):
        credentials = f"{self._app_id}:{self._app_secret}"
        base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )
        return {"Authorization": f"Basic {base64_credentials}"}

    def get_token(self):
        headers = self._generate_auth_header()
        headers.update(
            {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
        )
        response = requests.post(
            self._base_url + "oauth/token",
            headers=headers,
            data={"scope": "ecommerce", "grant_type": "client_credentials"},
        )
        response.raise_for_status()
        self._token = response.json()["access_token"]
        self._headers["Authorization"] = f"Bearer {self._token}"

    def _make_request(self, method, endpoint, data=None, params=None):
        url = self._base_url + endpoint
        response = requests.request(
            method, url, headers=self._headers, json=data, params=params
        )
        if response.status_code == 401:
            self.get_token()
            response = requests.request(
                method, url, headers=self._headers, json=data, params=params
            )
        response.raise_for_status()
        return response.json()

    def _get(self, endpoint, params=None):
        return self._make_request("GET", endpoint, params=params)

    def _post(self, endpoint, data):
        return self._make_request("POST", endpoint, data=data)

    def _patch(self, endpoint, data):
        return self._make_request("POST", endpoint, data=data)

    def list_invoices(self, page=1, include_items=False):
        endpoint = "invoices"
        params = {"page[number]": page, "include": "items" if include_items else None}
        return self._get(endpoint, params=params)["data"]

    def get_invoice(self, invoice_id):
        endpoint = f"invoices/{invoice_id}"
        return self._get(endpoint)["data"]

    def create_invoice(self, invoice_data):
        endpoint = "invoices"
        return self._post(endpoint, invoice_data)["data"]

    def update_invoice(self, invoice_id, update_data):
        endpoint = f"invoices/{invoice_id}"
        response = self._patch(endpoint, data=update_data)
        return response["data"]

    def list_contacts(self, page=1):
        endpoint = "contacts"
        params = {"page[number]": page}
        response = self._get(endpoint, params=params)
        return response["data"]
