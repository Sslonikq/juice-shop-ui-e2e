# juice-shop-ui-e2e

[![CI](https://github.com/Sslonikq/juice-shop-ui-e2e/actions/workflows/ci.yml/badge.svg)](https://github.com/Sslonikq/juice-shop-ui-e2e/actions/workflows/ci.yml)

UI/E2E-автоматизация [OWASP Juice Shop](https://owasp-juice.shop/) на **Playwright + Python + pytest**.

**[Отчёт Allure по последнему прогону](https://sslonikq.github.io/juice-shop-ui-e2e/)** - публикуется автоматически из CI.

Juice Shop взят не как объект security-тестирования, а как реалистичное веб-приложение на Angular: со всплывающими баннерами, снек-барами, `aria-label`, перебивающими видимый текст, и многошаговым чекаутом. То есть со всем, что обычно и делает UI-тесты нестабильными.

## Что здесь показано

- **Component Page Object Model** - страницы и переиспользуемые компоненты разделены, God Object отсутствует
- **Fluent API** - метод возвращает следующий Page Object, тест читается как сценарий
- **API-Bypass** - предусловия готовятся запросами, сценарий проходит через UI
- **Фикстуры pytest** с цепочкой зависимостей вместо копипасты в тестах
- **Изоляция через BrowserContext** - у каждого теста своё состояние, общих `Page` нет
- **Стабильные локаторы** по accessibility-дереву, без привязки к DOM Angular Material
- **Allure** со скриншотом и trace, прикреплёнными к упавшему тесту автоматически
- **CI на трёх браузерах** с публикацией отчёта на GitHub Pages
- **ruff + mypy strict** как обязательный этап пайплайна

## Стек

| | |
|---|---|
| Язык | Python 3.13 |
| Браузерная автоматизация | Playwright 1.62 (sync API) |
| Тест-раннер | pytest 9.1 + pytest-playwright |
| Отчёты | Allure |
| Данные | Faker + фабрики |
| Качество кода | ruff, mypy (strict) |
| Приложение под тестом | Juice Shop v20.2.0 в Docker |

## Быстрый старт

**1. Поднять приложение**

```bash
docker compose up -d --wait
```

`--wait` не отдаёт управление, пока healthcheck не подтвердит готовность. Версия образа зафиксирована: `latest` не использовать, новые релизы ломают локаторы без единой правки в тестах.

**2. Установить зависимости**

```bash
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # Linux / macOS
pip install -r requirements.txt
playwright install
```

**3. Настроить окружение**

```bash
cp .env.example .env
```

Единственная переменная - `BASE_URL`. Значение по умолчанию подходит для локального Docker.

**4. Запустить**

```bash
pytest
```

## Запуск тестов

```bash
pytest                                        # всё, headless chromium
pytest --headed                               # с видимым браузером
pytest --browser firefox                      # другой браузер
pytest --browser chromium --browser firefox --browser webkit
pytest -m smoke                               # по маркеру
pytest tests/e2e                              # по пути
pytest --slowmo 500 --headed                  # замедленно, для отладки
```

Маркеры: `smoke`, `auth`, `e2e`, `purchase`. Незарегистрированный маркер не пройдёт - включён `--strict-markers`.

## Отчёты

Trace и скриншоты собираются автоматически - флаги прописаны в `pyproject.toml`, задавать руками не нужно.

```bash
pytest
allure serve allure-results        # открыть отчёт локально
```

Для локального просмотра нужен [Allure CLI](https://allurereport.org/docs/install/) - это Java-приложение, отдельно от Python-пакетов.

Что попадает в отчёт при падении:

| артефакт | когда |
|---|---|
| скриншот | тест упал, браузер ещё жив |
| trace.zip | после закрытия контекста, когда файл записан на диск |
| шаги сценария | всегда, через `@allure.step` |

Скриншот и trace прикрепляются из хука `pytest_runtest_makereport` в [tests/conftest.py](tests/conftest.py). Разделение по фазам не случайное: снимок делается на фазе `call`, пока браузер жив, а trace - на `teardown`, потому что Playwright дописывает файл только при закрытии контекста.

## Структура

```
src/
  pages/        home, login, basket, address, delivery,
                payment, order_summary, order_confirmation
  components/   header, toast
  api/          api_client      - регистрация, логин, адрес, карта
  models/       user, auth_session, address, payment_card  (frozen dataclasses)
  factories/    user, address, payment_card
  config/       settings        - единственная точка чтения env
tests/
  conftest.py           - фикстуры и хуки Allure
  smoke/                - витрина отвечает и отдаёт товары
  auth/                 - логин через UI, вход через API-bypass
  e2e/                  - покупка целиком через UI
docker-compose.yml      - Juice Shop с зафиксированным тегом и healthcheck
.github/workflows/      - CI
```

## Как выглядит тест

```python
def test_purchase(buyer_page: Page) -> None:
    order_confirmation = (
        HomePage(buyer_page)
        .add_first_product_to_basket()
        .open_basket()
        .checkout()
        .select_first_address()
        .proceed()
        .select_first_delivery_method()
        .proceed()
        .select_first_card()
        .proceed()
        .place_order()
    )

    order_confirmation.assert_order_created()
```

Ни одного локатора и ни одного `wait`. Фикстура `buyer_page` отдаёт страницу, где пользователь уже зарегистрирован, авторизован, а адрес и карта заведены - всё через API, потому что это предусловие, а не проверяемое поведение.

## Архитектурные решения

**Граница проходит по роли действия, а не по тесту.** Сценарий идёт через UI, предусловие - через API. Тест логина заполняет форму кликами, потому что это и есть проверяемое поведение, но пользователя для него создаёт API-фикстура. Регистрация через UI означала бы проверку двух функций сразу и падение логин-теста из-за поломки в регистрации.

**Fluent API ради читаемости, а не ради паттерна.** Метод возвращает тот Page Object, на который пользователь реально попал. Если экран не сменился - возвращается `self`. Отсюда цепочка выше читается как маршрут по приложению.

**Action и assertion разделены.** `add_to_basket()` делает, `assert_order_created()` проверяет. Проверки не прячутся внутри действий.

**Локаторы по accessibility-дереву.** Приоритет `get_by_role` → `get_by_label` → `get_by_text`, CSS и XPath - в последнюю очередь. Результат проверяем: три браузера прошли без единой правки локаторов.

**Ожидания - только автоматические.** `expect` из Playwright ретраится сам. `wait_for_timeout` и `time.sleep` в проекте отсутствуют: если элемент не появляется, ищется причина, а не растится таймаут.

**Состояние умирает вместе с контейнером.** Томов в compose нет намеренно. Juice Shop пишет пользователей и заказы в SQLite внутри контейнера, и переживший прогон контейнер стартует с загрязнённой базы - накопленные юзеры, разобранные `Only 1 left` товары. Прогон N+1 переставал бы повторять прогон N.

## CI

Три job'а в [.github/workflows/ci.yml](.github/workflows/ci.yml):

```
quality  ruff check → ruff format --check → mypy
   ↓
e2e      матрица [chromium, firefox, webkit], fail-fast отключён
         docker compose up --wait → pytest → артефакты
   ↓
report   собрать результаты трёх браузеров → подложить историю
         → allure generate → опубликовать на GitHub Pages
```

- **Матрица, а не три `--browser` в одном прогоне** - упавший браузер видно по имени job'а, остальные не глушатся.
- **Lint отдельным job'ом** - браузеры ему не нужны, и опечатка отсекается за полминуты вместо четырёх.
- **`report` выполняется и при красных тестах** - отчёт нужен именно тогда. При этом `e2e` честно краснеет: падение не заглушается.
- **История прогонов** переносится из ветки `gh-pages` в результаты перед генерацией - отсюда график трендов в отчёте.

## Особенности Juice Shop v20.2.0

Найдено разведкой. Экономит часы отладки тому, кто возьмётся за это приложение:

- **Авторизация живёт в трёх местах**: cookie `token`, `localStorage.token` и `sessionStorage.bid`. `storage_state` Playwright не умеет `sessionStorage`, поэтому оба хранилища заполняются через `add_init_script` до первой навигации. Без `bid` пользователь выглядит вошедшим, но корзина не работает.
- **Баннеры гасятся куками**: `welcomebanner_status=dismiss`, `cookieconsent_status=dismiss`. Без них два диалога перекрывают страницу и клики падают по таймауту. `language=en` убирает всплывашку, перехватывающую клик на checkout.
- **`aria-label` перебивает видимый текст**: кнопка с надписью «Place your order and pay» ищется по имени `Complete your purchase`.
- **Названия кнопок не соответствуют маршруту**: «Proceed to payment selection» ведёт на выбор доставки. Маршрут определяется по фактическому URL.
- **Строка в таблице выбирается только через `radio.check()`** - клик по строке оставляет кнопку `disabled`.
- **После «Add to Basket» нужно дождаться снек-бара** - иначе корзина откроется пустой.
- **`get_by_role(name=...)` совпадает по подстроке**: `name="Login"` цепляет и «Login with Google». Нужен `exact=True`.

## Качество кода

```bash
ruff check .
ruff format --check .
mypy
```

`mypy` в режиме `strict`: аннотации обязательны на всех публичных методах Page Object и API-клиента. Без них Page Object перестаёт быть контрактом.

Те же три команды выполняет job `quality` в CI.
