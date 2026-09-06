from playwright.sync_api import APIRequestContext

from src.models.address import Address
from src.models.auth_session import AuthSession
from src.models.payment_card import PaymentCard


class ApiClient:
    def __init__(self, request: APIRequestContext) -> None:
        self._request = request

    def register_user(self, email: str, password: str) -> None:
        response = self._request.post(
            "/api/Users",
            data={
                "email": email,
                "password": password,
                "passwordRepeat": password,
                "securityQuestion": {"id": 1},
                "securityAnswer": "test",
            },
        )
        if not response.ok:
            raise RuntimeError(
                f"User registration failed: POST /api/Users -> "
                f"{response.status} {response.text()}"
            )

    def login(self, email: str, password: str) -> AuthSession:
        response = self._request.post(
            "/rest/user/login",
            data={
                "email": email,
                "password": password,
            },
        )
        if not response.ok:
            raise RuntimeError(
                f"User login failed: POST /rest/user/login -> "
                f"{response.status} {response.text()}"
            )
        authentication = response.json()["authentication"]
        return AuthSession(
            token=authentication["token"],
            basket_id=str(authentication["bid"]),
        )

    def create_address(self, address: Address, token: str) -> None:
        response = self._request.post(
            "/api/Addresss",
            data={
                "fullName": address.full_name,
                "mobileNum": address.mobile_number,
                "zipCode": address.zip_code,
                "streetAddress": address.street_address,
                "city": address.city,
                "state": address.state,
                "country": address.country,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        if not response.ok:
            raise RuntimeError(
                f"Address creation failed: POST /api/Addresss -> "
                f"{response.status} {response.text()}"
            )

    def create_payment_card(self, card: PaymentCard, token: str) -> None:
        response = self._request.post(
            "/api/Cards",
            data={
                "fullName": card.full_name,
                "cardNum": card.card_number,
                "expMonth": card.expiry_month,
                "expYear": card.expiry_year,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        if not response.ok:
            raise RuntimeError(
                f"Card creation failed: POST /api/Cards -> "
                f"{response.status} {response.text()}"
            )
