from playwright.sync_api import APIRequestContext


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
