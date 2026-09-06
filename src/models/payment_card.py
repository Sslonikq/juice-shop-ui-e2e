from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentCard:
    full_name: str
    card_number: int
    expiry_month: str
    expiry_year: str
