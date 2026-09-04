# juice-shop-ui-e2e

Production-like фреймворк для UI/E2E-автоматизации [OWASP Juice Shop](https://owasp-juice.shop/) (намеренно уязвимое учебное веб-приложение на Angular/Node/Express) на **Playwright + Python + pytest**. Juice Shop используется не как объект security-тестирования, а как реалистичное web-приложение для демонстрации качественного automation-фреймворка: Component Page Object Model, Fluent API, pytest-фикстуры, API-Bypass, стабильные локаторы, изоляция browser context, диагностика flaky-тестов, trace/report, CI. Основной сценарий — покупка товара в Juice Shop.

Используется **синхронный** Playwright API (`playwright.sync_api`) — он же используется плагином `pytest-playwright`. Async-вариант не смешивать с sync в одном проекте.

## Как это работает (слои)

```
test → Page Object → Component Object → Playwright Page/BrowserContext → Juice Shop UI
```

Подготовка состояния — в обход UI:
```
test/fixture → API Client → Juice Shop REST API
```

Авторизация для не-auth тестов:
```
API → token/authentication → BrowserContext storage state → authenticated UI session
```

Тест описывает intent пользователя, а не DOM:
```python
(
    home_page
    .search_for("Apple Juice")
    .open_product("Apple Juice")
    .add_to_basket()
    .open_basket()
    .proceed_to_checkout()
    .place_order()
    .assert_order_created()
)
```
Никаких сырых `page.locator(...).click()` в тестах без необходимости.

## Ключевые архитектурные решения (важно не сломать)

- **Component POM, не God Object.** Повторяющиеся куски UI (`Header`, `NavigationMenu`, `Basket`, `ProductCard`, `LoginForm`, `Toast`) — отдельные Component Object. Page Object знает страницу, Component — свой кусок. `BasePage` не должен разрастаться в класс на все локаторы приложения.
- **Тест = бизнес-сценарий, не DOM-механика.** «Найти товар → добавить в корзину → оформить заказ», а не «найти `mat-card` → нажать кнопку».
- **Fluent API — ради читаемости, не ради паттерна.** Методы возвращают логически следующий Page/Component Object, не `self` просто чтобы продолжить цепочку. Длинную цепочку можно и нужно разбивать на переменные, если так понятнее.
- **Action и assertion разделены.** `add_to_basket()` делает действие, `assert_product_in_basket()` проверяет результат — не прятать проверки внутри action-методов.
- **API-Bypass — только для setup, не подмена UI-сценария.** Если тест не проверяет сам Login, пользователь заходит уже авторизованным через API/storage state. Но если тест проверяет именно логин или покупку — это делается через UI, API-Bypass туда не лезет. `Login test → UI auth`, `Purchase E2E → API auth + UI purchase` — принципиальное разделение, не смешивать.
- **Уязвимости Juice Shop — не механизм тестового setup.** Не эксплуатировать vulnerability ради подготовки данных, если есть нормальный API.
- **Не полагаться на публичный demo-инстанс.** Для стабильных прогонов — локальный/контролируемый Juice Shop (Docker), у публичного demo нет гарантии uptime.
- **BrowserContext — граница изоляции теста.** Никаких общих mutable `Page`/глобального состояния между тестами; `storage_state`, если используется, не должен "утекать" в другие тесты. Никаких module/session-scoped фикстур, отдающих один `Page` нескольким тестам.
- **Auto-waiting Playwright, не `page.wait_for_timeout()` и не `time.sleep()`.** Если элемент не появляется — искать реальную причину (locator/UI state/network race/анимация), а не растить таймаут.
- **Локаторы по приоритету:** `get_by_role` → `get_by_label` → `get_by_placeholder` → `get_by_text` → `get_by_test_id` → CSS/XPath в последнюю очередь. Не завязываться на внутреннюю DOM-структуру Angular Material (`mat-card:nth-child(4)` и т.п.).
- **Ассерты — через `expect` из `playwright.sync_api`**, не через голый `assert` по мгновенному состоянию: `expect` умеет ретраиться и убирает целый класс flaky. Проверяют пользовательский результат, не внутренности Angular-компонентов.
- **Тестовые данные — через factories/builders (Faker внутри), не инлайн-рандом** в каждом тесте. Сгенерированные данные должны быть видны в отчёте при падении.
- **Cleanup — предпочтительно через API**, не через UI, если результат тот же.
- **Конфигурация — через env** (`.env` + `python-dotenv`), URL/credentials никогда не в тестах. В env только `BASE_URL` — производные пути (`/rest`, `/api`) не выносить в переменные, они не конфигурация, а знание об API.
- **Типы обязательны.** Аннотации на публичных методах Page/Component Object и API-клиента, проверка через `mypy`. Без них Page Object перестаёт быть контрактом.
- **CLAUDE.md описывает целевую архитектуру, а не текущее состояние репозитория** — не считать слой реализованным, пока он реально не написан.

## Структура

```
src/
  pages/        login_page.py, home_page.py, search_page.py, product_page.py,
                basket_page.py, checkout_page.py, order_confirmation_page.py
  components/   header.py, navigation_menu.py, search_bar.py, product_card.py,
                basket_item.py, basket_summary.py, login_form.py, user_menu.py, toast.py
  api/          api_client.py, auth_api.py, basket_api.py, user_api.py — не знают про page.get_by_role(...)
                знание про namespace API живёт здесь, см. «API Juice Shop»
  models/       user.py, product.py, address.py, order.py  (dataclasses)
  factories/    user_factory.py, address_factory.py
  config/       settings.py — единственная точка чтения env
  utils/        logger.py
tests/
  conftest.py              — общие фикстуры (page objects, auth, данные)
  auth/test_login.py       — логин через UI
  e2e/test_purchase.py     — покупка: API auth + UI purchase flow
  smoke/test_smoke.py
pyproject.toml / requirements.txt / .env.example / .gitignore
```
Целевая структура, не обязательный список файлов — abstraction layer не создаётся до реальной потребности.

Именование: файлы и методы `snake_case`, классы `PascalCase`, тестовые файлы `test_*.py`, тестовые функции `test_*`.

Язык: комментарии и docstring — русские, но всё, что печатается в рантайме (текст исключений, логи, сообщения ассертов) — **на английском**. Консоль Windows выводит их не в UTF-8, и русский текст превращается в мусор именно там, где он нужнее всего — в логе упавшего CI-прогона.

Границы слоёв жёсткие: Page Object не делает HTTP-запросов, API Client не знает `page.get_by_role(...)`.

Фикстуры живут в `conftest.py` (общие) и рядом с тестами (специфичные). Фикстура создаёт зависимость, а не прячет в себе половину сценария.

## Запуск

Juice Shop локально — **версия зафиксирована**, `latest` не использовать: новые релизы (например редизайн storefront в v20.0.0) ломают UI-контракты без единого изменения в тестах.

```bash
docker run -d --rm -p 3000:3000 --name juice-shop bkimminich/juice-shop:v20.2.0
curl http://localhost:3000/rest/admin/application-version   # {"version":"20.2.0"}
```

`--rm` — осознанно, и локально тоже. Juice Shop мутирует своё состояние во время прогона (пользователи, корзины, заказы пишутся в SQLite внутри контейнера). Переживший остановку контейнер стартует с загрязнённой базы: накопленные тестовые юзеры, чужие корзины, разобранные `Only 1 left` товары — и прогон N+1 отличается от прогона N без единого изменения в коде. Пересоздание стоит секунды, образ уже в кэше.

## API Juice Shop

Namespace не делится по смыслу — префикс нужно знать поэндпоинтно. Проверено на v20.2.0:

| эндпоинт | назначение |
|---|---|
| `POST /rest/user/login` | логин, возвращает JWT |
| `POST /api/Users` | регистрация |
| `GET /api/Products` | каталог (Sequelize-автогенерация) |
| `GET /rest/products/search?q=` | поиск |
| `GET/POST /rest/basket/{id}` | корзина |
| `GET/POST /api/Addresss` | адреса (в приложении реально три `s`) |
| `GET /rest/admin/application-version` | версия приложения |

Поэтому в env только `BASE_URL`; `/rest` и `/api` — забота `ApiClient`, а не конфигурации. Переменной `API_URL` быть не должно: она создаёт иллюзию единого префикса, которого нет.

Тесты:
```bash
python -m venv venv
venv\Scripts\activate              # Windows;  source venv/bin/activate — Linux/macOS
pip install -r requirements.txt
playwright install
pytest
```
Команды документировать по факту работоспособности, не заранее.

`.env` (не коммитится) / `.env.example` (коммитится):
```
BASE_URL=http://localhost:3000
TEST_USER_EMAIL=
TEST_USER_PASSWORD=
```
Credentials — никогда в тестах/Page Object/фикстурах/git/скриншотах/логах.

## CI

```
checkout → setup Python → pip install -r requirements.txt → playwright install --with-deps
  → start Juice Shop (зафиксированный тег) → wait until ready → lint → typecheck → pytest
  → upload report/trace/screenshots
```
При падении теста должны быть доступны trace + screenshot (+video при включении) — чтобы понять, что делал тест, где упал и на каком локаторе/действии. Включается флагами `pytest-playwright`: `--tracing retain-on-failure --screenshot only-on-failure`.

## Кросс-браузер

Минимум Chromium/Firefox/WebKit (`--browser chromium --browser firefox --browser webkit`), добавляется осознанно — не плодить отдельные Page Object под каждый браузер без реальной причины; browser-specific ограничения документировать явно.

## Тест-маркеры

Только по факту использования: `smoke`, `e2e`, `auth`, `purchase`, `regression`, `slow`. Каждый маркер регистрируется в `pyproject.toml` (`--strict-markers` не даст использовать незарегистрированный). Маркер без реального use case — удалить.

## Анти-паттерны

Не делать: DOM-стройку прямо в тесте вместо Page Object; `BasePage` со всеми локаторами приложения; HTTP-вызов внутри Page Object-метода (`add_to_basket()`, дергающий REST вместо UI); `wait_for_timeout()`/`time.sleep()` для лечения flaky; `try/except` с проглатыванием ошибки клика; проверку UI purchase flow через `API create order → API confirm → UI assert`; весь suite, зависящий от одного глобального авторизованного пользователя; session-scoped фикстуру с общим `Page`.

## Процесс добавления фичи

1. Определить пользовательский сценарий и что в нём UI-behavior, а что setup/teardown.
2. Определить Page Object, выделить переиспользуемые Component Objects, подобрать стабильные локаторы.
3. Решить, нужен ли API-Bypass; завести фикстуру/фабрику для данных.
4. Реализовать минимально нужную абстракцию, написать E2E-тест с ассертами на бизнес-результат.
5. Прогнать тест локально, затем релевантный suite, затем lint/typecheck.
6. Обновить README/CI только если изменилось поведение проекта; коммитить только после зелёного прогона.

Без попутных архитектурных рефакторингов без конкретной причины.

## Текущий статус / не-цели

Репозиторий с нуля, стадии:

1. Python+pytest+Playwright setup ✅
2. Juice Shop local env (v20.2.0 в Docker) ✅
3. Smoke-тест — первый рабочий прогон, минимум абстракций
4. Page Objects + Component Objects — по мере надобности, не авансом
5. ApiClient — минимальный, только регистрация пользователя: появился первый потребитель
6. Login UI test — **сценарий** целиком через UI, пользователь для него создаётся через API
7. API auth bypass (storage state)
8. Purchase E2E — API auth + UI purchase
9. Fluent API → cross-browser → reporting/trace → CI → hardening

Граница проходит не по тесту, а по роли действия: **сценарий — через UI, предусловие — через API**. Login UI test заполняет форму кликами (это проверяемое поведение), но пользователя для него регистрирует API-фикстура (это setup). Регистрировать через UI значило бы проверять в одном тесте две функции сразу и валить login-тест из-за поломки в регистрации.

`ApiClient` пишется не авансом: на шаге 5 у него ровно один метод, потому что нужен ровно один. Остальные добавляются, когда появляются потребители.

Вне скоупа: Selenium/Cypress, TypeScript/JS-стек, `unittest` вместо `pytest`, монолитный Page Object, полноценный security/pentesting-фреймворк, автоматизация hacking challenges Juice Shop, эксплуатация уязвимостей как цель automation, load/performance testing, полноценный visual regression (если не запрошен отдельно), LLM/AI-слой, интеграция с БД без конкретной нужды, произвольные сторонние сервисы.

Формула проекта: **Playwright + Python/pytest + Component POM + Fluent API + API-Bypass + фикстуры + isolated BrowserContext + stable locators + business assertions = production-like UI/E2E framework.**
