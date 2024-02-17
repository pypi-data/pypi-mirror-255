import datetime


class CheckoutSessionLineItem:
    def __init__(
        self,
        name: str,
        description: str,
        image: str,
        price: float,
        quantity: int,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.image = image
        self.price = price
        self.quantity = quantity

    def dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "price": self.price,
            "quantity": self.quantity,
        }


class CheckoutSession:
    def __init__(
        self,
        uuid: str,
        line_items: list,
        total_amount: str,
        success_url: str,
        cancel_url: str,
        client_reference_id: str,
        webhook_url: str,
        checkout_page_token: str,
        url: str,
        active: bool,
        status: str,
        expires_at: str,
        metadata: dict,
    ):
        self.uuid = uuid
        self.line_items = [CheckoutSessionLineItem(**item) for item in line_items]
        self.total_amount = total_amount
        self.success_url = success_url
        self.cancel_url = cancel_url
        self.client_reference_id = client_reference_id
        self.webhook_url = webhook_url
        self.checkout_page_token = checkout_page_token
        self.url = url
        self.expires_at = datetime.datetime.fromisoformat(expires_at[:-1])  # Remove Z
        self.active = active
        self.status = status
        self.metadata = metadata

    def link(self) -> str:
        return f"{self.url}"
