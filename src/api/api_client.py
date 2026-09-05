from playwright.sync_api import APIRequestContext

from src.models.auth_session import AuthSession


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
