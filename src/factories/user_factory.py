from uuid import uuid4

from src.models.user import User

_PASSWORD = "Str0ngPass!23"


class UserFactory:
    @staticmethod
    def build() -> User:
        return User(
            email=f"user-{uuid4().hex[:8]}@juice.test",
            password=_PASSWORD,
        )
