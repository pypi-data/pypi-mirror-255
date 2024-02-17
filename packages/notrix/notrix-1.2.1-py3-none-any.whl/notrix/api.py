from typing import List

import requests
from .models import CheckoutSessionLineItem, CheckoutSession


class Client:
    BASE_URL = "https://api.notrix.io"

    def __init__(self, secret_api_key: str):
        self.secret_api_key = secret_api_key

    def _auth_headers(self) -> dict:
        return {f"Authorization": f"Token {self.secret_api_key}"}

    def _make_request(self, method: str, path: str, **kwargs):
        request_path = f"{self.BASE_URL}/{path}"
        headers = kwargs.pop("headers", {})
        headers.update(self._auth_headers())
        return requests.request(method, request_path, headers=headers, **kwargs)

    def create_checkout_session(
        self,
        items: List[CheckoutSessionLineItem],
        success_url: str,
        cancel_url: str,
        client_reference_id: str = None,
        webhook_url: str = None,
    ):
        params = {
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [item.dict() for item in items],
        }
        if client_reference_id is not None:
            params.update({"client_reference_id": client_reference_id})
        if webhook_url is not None:
            params.update({"webhook_url": webhook_url})

        response = self._make_request(
            method="post",
            path="console/checkout-sessions/",
            json=params,
        )

        response.raise_for_status()

        return CheckoutSession(**response.json())

    def is_paid(self, checkout_page_token: str) -> bool:
        response = self._make_request(
            method="get",
            path="console/check-payment-status/",
            params={"token": checkout_page_token},
        )
        response.raise_for_status()

        return response.json()["payment_confirmed"]
