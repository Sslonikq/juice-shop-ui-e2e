# juice-shop-ui-e2e

Production-like фреймворк для UI/E2E-автоматизации [OWASP Juice Shop](https://owasp-juice.shop/) (намеренно уязвимое учебное веб-приложение на Angular/Node/Express) на Playwright + TypeScript. Juice Shop используется не как объект security-тестирования, а как реалистичное web-приложение для демонстрации качественного automation-фреймворка: Component Page Object Model, Fluent API, Playwright fixtures, API-Bypass, стабильные локаторы, изоляция browser context, диагностика flaky-тестов, trace/report, CI. Основной сценарий — покупка товара в Juice Shop.

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
```typescript
await homePage
  .searchFor("Apple Juice")
  .openProduct("Apple Juice")
  .addToBasket()
  .openBasket()
  .proceedToCheckout()
  .placeOrder()
  .assertOrderCreated();
```
Никаких сырых `page.locator(...).click()` в тестах без необходимости.

## Ключевые архитектурные решения (важно не сломать)

- **Component POM, не God Object.** Повторяющиеся куски UI (`Header`, `NavigationMenu`, `Basket`, `ProductCard`, `LoginForm`, `Toast`) — отдельные Component Object. Page Object знает страницу, Component — свой кусок. `BasePage` не должен разрастаться в класс на все локаторы приложения.
- **Тест = бизнес-сценарий, не DOM-механика.** «Найти товар → добавить в корзину → оформить заказ», а не «найти `mat-card` → нажать кнопку».
- **Fluent API — ради читаемости, не ради паттерна.** Методы возвращают логически следующий Page/Component Object, не `this` просто чтобы продолжить цепочку. Длинную цепочку можно и нужно разбивать на переменные, если так понятнее.
- **Action и assertion разделены.** `addToBasket()` делает действие, `assertProductInBasket()` проверяет результат — не прятать проверки внутри action-методов.
- **API-Bypass — только для setup, не подмена UI-сценария.** Если тест не проверяет сам Login, пользователь заходит уже авторизованным через API/storage state. Но если тест проверяет именно логин или покупку — это делается через UI, API-Bypass туда не лезет. `Login test → UI auth`, `Purchase E2E → API auth + UI purchase` — принципиальное разделение, не смешивать.
- **Уязвимости Juice Shop — не механизм тестового setup.** Не эксплуатировать vulnerability ради подготовки данных, если есть нормальный API.
- **Не полагаться на публичный demo-инстанс.** Для стабильных прогонов — локальный/контролируемый Juice Shop (Docker), у публичного demo нет гарантии uptime.
- **BrowserContext — граница изоляции теста.** Никаких общих mutable `Page`/глобального состояния между тестами; `storageState`, если используется, не должен "утекать" в другие тесты.
- **Auto-waiting Playwright, не `waitForTimeout()`.** Если элемент не появляется — искать реальную причину (locator/UI state/network race/анимация), а не растить таймаут.
- **Локаторы по приоритету:** `getByRole` → `getByLabel` → `getByPlaceholder` → `getByText` → `getByTestId` → CSS/XPath в последнюю очередь. Не завязываться на внутреннюю DOM-структуру Angular Material (`mat-card:nth-child(4)` и т.п.).
- **Ассерты проверяют пользовательский результат**, не внутренности Angular-компонентов.
- **Тестовые данные — через factories/builders (Faker внутри), не инлайн-рандом** в каждом тесте. Сгенерированные данные должны быть видны в отчёте при падении.
- **Cleanup — предпочтительно через API**, не через UI, если результат тот же.
- **Конфигурация — через env**, URL/credentials никогда не в spec-файлах.
- **CLAUDE.md описывает целевую архитектуру, а не текущее состояние репозитория** — не считать слой реализованным, пока он реально не написан.

## Структура

```
src/
  pages/        LoginPage, HomePage, SearchPage, ProductPage, BasketPage, CheckoutPage, OrderConfirmationPage
  components/   Header, NavigationMenu, SearchBar, ProductCard, BasketItem, BasketSummary, LoginForm, UserMenu, Toast
  api/          ApiClient, AuthApi, BasketApi, UserApi — не знают про page.getByRole(...)
  models/       User, Product, Address, Order
  factories/    UserFactory, AddressFactory
  fixtures/     auth.fixture, pages.fixture, data.fixture — создают зависимости, не прячут в себе половину сценария
  config/       env.ts
  utils/        logger.ts
tests/
  auth/login.spec.ts       — логин через UI
  e2e/purchase.spec.ts     — покупка: API auth + UI purchase flow
  smoke/smoke.spec.ts
playwright.config.ts / package.json / tsconfig.json / .env.example / .gitignore
```
Целевая структура, не обязательный список файлов — abstraction layer не создаётся до реальной потребности.

Границы слоёв жёсткие: Page Object не делает `request.post(...)`, API Client не знает `page.getByRole(...)`.

## Запуск

Juice Shop локально:
```bash
docker pull bkimminich/juice-shop
docker run --rm -p 3000:3000 bkimminich/juice-shop
# http://localhost:3000
```
Версию приложения фиксировать для стабильного CI — новые релизы (например v20.0.0 с редизайном storefront) ломают UI-контракты.

Тесты:
```bash
npm ci
npx playwright install --with-deps
npm run lint
npm run typecheck
npx playwright test
npx playwright show-report
```
Команды документировать по факту наличия в `package.json`, не заранее.

`.env` (не коммитится) / `.env.example` (коммитится):
```
BASE_URL=http://localhost:3000
API_URL=http://localhost:3000/api
TEST_USER_EMAIL=
TEST_USER_PASSWORD=
```
Credentials — никогда в spec/Page Object/fixture/git/скриншотах/логах.

## CI

```
checkout → setup Node → npm ci → install Playwright browsers → start Juice Shop
  → wait until ready → lint → typecheck → playwright test → upload report/trace/screenshots
```
При падении теста должны быть доступны trace + screenshot (+video при включении) — чтобы понять, что делал тест, где упал и на каком локаторе/действии.

## Кросс-браузер

Минимум Chromium/Firefox/WebKit, добавляется осознанно — не плодить отдельные Page Object под каждый браузер без реальной причины; browser-specific ограничения документировать явно.

## Тест-теги

Только по факту использования: `@smoke @e2e @auth @purchase @regression @slow`. Тег без реального use case — удалить.

## Анти-паттерны

Не делать: DOM-стройку прямо в тесте вместо Page Object; `BasePage` со всеми локаторами приложения; API-вызов внутри Page Object-метода (`addToBasket()`, дергающий REST вместо UI); `waitForTimeout()` для лечения flaky; `try/catch` с проглатыванием ошибки клика; проверку UI purchase flow через `API create order → API confirm → UI assert`; весь suite, зависящий от одного глобального авторизованного пользователя.

## Процесс добавления фичи

1. Определить пользовательский сценарий и что в нём UI-behavior, а что setup/teardown.
2. Определить Page Object, выделить переиспользуемые Component Objects, подобрать стабильные локаторы.
3. Решить, нужен ли API-Bypass; завести fixture/factory для данных.
4. Реализовать минимально нужную абстракцию, написать E2E-тест с ассертами на бизнес-результат.
5. Прогнать тест локально, затем релевантный suite, затем lint/typecheck.
6. Обновить README/CI только если изменилось поведение проекта; коммитить только после зелёного прогона.

Без попутных архитектурных рефакторингов без конкретной причины.

## Текущий статус / не-цели

Репозиторий с нуля, стадии: Playwright+TS setup → Juice Shop local env → Page Objects → Component Objects → fixtures/factories → API client → API auth bypass → Login UI test → Purchase E2E → Fluent API → cross-browser → reporting/trace → CI → hardening.

Вне скоупа: Selenium/Cypress, JS вместо TS, монолитный Page Object, полноценный security/pentesting-фреймворк, автоматизация hacking challenges Juice Shop, эксплуатация уязвимостей как цель automation, load/performance testing, полноценный visual regression (если не запрошен отдельно), LLM/AI-слой, интеграция с БД без конкретной нужды, произвольные сторонние сервисы.

Формула проекта: **Playwright + TypeScript + Component POM + Fluent API + API-Bypass + Fixtures + isolated BrowserContext + stable locators + business assertions = production-like UI/E2E framework.**
