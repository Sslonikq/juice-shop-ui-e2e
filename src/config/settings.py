"""Единственная точка чтения окружения.

Остальные слои берут конфигурацию отсюда и никогда не трогают ``os.environ``
напрямую — иначе URL и credentials расползаются по тестам и Page Object.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Путь считается от файла, а не от текущей директории: pytest можно запускать
# откуда угодно, .env всё равно будет найден в корне репозитория.
_REPO_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(_REPO_ROOT / ".env")


def _required(name: str) -> str:
    """Вернуть значение переменной окружения или упасть с внятной ошибкой.

    Молчаливый дефолт здесь недопустим: на пустом окружении тесты стартовали бы
    против чужого адреса и зеленели. Зелёный тест, проверивший не то приложение,
    хуже красного.
    """
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable {name} is not set. "
            f"Copy .env.example to .env and fill in the values."
        )
    return value


BASE_URL: str = _required("BASE_URL")
