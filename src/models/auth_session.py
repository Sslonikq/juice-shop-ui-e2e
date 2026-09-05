from dataclasses import dataclass


@dataclass(frozen=True)
class AuthSession:
    token: str
    basket_id: str