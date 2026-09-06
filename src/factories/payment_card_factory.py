from faker import Faker

from src.models.payment_card import PaymentCard

_faker = Faker()

_CARD_NUMBER = 4111111111111111
_EXPIRY_MONTH = "12"
_EXPIRY_YEAR = "2099"


class PaymentCardFactory:
    @staticmethod
    def build() -> PaymentCard:
        return PaymentCard(
            full_name=_faker.name(),
            card_number=_CARD_NUMBER,
            expiry_month=_EXPIRY_MONTH,
            expiry_year=_EXPIRY_YEAR,
        )
