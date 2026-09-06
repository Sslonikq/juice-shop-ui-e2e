import json
import re
from collections.abc import Generator, Iterator
from pathlib import Path

import allure
import pytest
from playwright.sync_api import APIRequestContext, BrowserContext, Page, Playwright

from src.api.api_client import ApiClient
from src.config.settings import BASE_URL
from src.factories.address_factory import AddressFactory
from src.factories.payment_card_factory import PaymentCardFactory
from src.factories.user_factory import UserFactory
from src.models.auth_session import AuthSession
from src.models.user import User


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    report = yield

    if report.failed and report.when == "call":
        page: Page | None = getattr(item, "funcargs", {}).get("page")
        if page is not None:
            allure.attach(
                page.screenshot(full_page=True),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )

    if report.when == "teardown":
        _attach_trace(item)

    return report


def _slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()


def _attach_trace(item: pytest.Item) -> None:
    output_dir = Path(item.config.getoption("--output"))
    trace = output_dir / _slugify(item.nodeid) / "trace.zip"
    if trace.exists():
        allure.attach.file(str(trace), name="trace", extension="zip")


def _dismiss_banners(context: BrowserContext) -> None:
    context.add_cookies(
        [
            {"name": "welcomebanner_status", "value": "dismiss", "url": BASE_URL},
            {"name": "cookieconsent_status", "value": "dismiss", "url": BASE_URL},
            {"name": "language", "value": "en", "url": BASE_URL},
        ]
    )


@pytest.fixture
def api_request_context(playwright: Playwright) -> Iterator[APIRequestContext]:
    context = playwright.request.new_context(base_url=BASE_URL)
    yield context
    context.dispose()


@pytest.fixture
def api_client(api_request_context: APIRequestContext) -> ApiClient:
    return ApiClient(api_request_context)


@pytest.fixture
def registered_user(api_client: ApiClient) -> User:
    user = UserFactory.build()
    api_client.register_user(user.email, user.password)
    return user


@pytest.fixture
def auth_session(api_client: ApiClient, registered_user: User) -> AuthSession:
    return api_client.login(registered_user.email, registered_user.password)


@pytest.fixture
def storefront(page: Page) -> Page:
    _dismiss_banners(page.context)
    page.goto(BASE_URL)
    return page


@pytest.fixture
def authenticated_page(page: Page, auth_session: AuthSession) -> Page:
    context = page.context

    _dismiss_banners(context)
    context.add_cookies(
        [{"name": "token", "value": auth_session.token, "url": BASE_URL}]
    )
    context.add_init_script(
        f"localStorage.setItem('token', {json.dumps(auth_session.token)});"
        f"sessionStorage.setItem('bid', {json.dumps(auth_session.basket_id)});"
    )

    page.goto(BASE_URL)
    return page


@pytest.fixture
def buyer_page(
    authenticated_page: Page, api_client: ApiClient, auth_session: AuthSession
) -> Page:
    api_client.create_address(AddressFactory.build(), auth_session.token)
    api_client.create_payment_card(PaymentCardFactory.build(), auth_session.token)
    return authenticated_page
