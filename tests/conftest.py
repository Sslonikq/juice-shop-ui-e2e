import json
from collections.abc import Iterator

import pytest
from playwright.sync_api import APIRequestContext, Page, Playwright

from src.api.api_client import ApiClient
from src.config.settings import BASE_URL
from src.factories.address_factory import AddressFactory
from src.factories.payment_card_factory import PaymentCardFactory
from src.factories.user_factory import UserFactory
from src.models.auth_session import AuthSession
from src.models.user import User


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
    page.goto(BASE_URL)
    page.get_by_role("button", name="Close Welcome Banner").click()
    page.get_by_role("button", name="dismiss cookie message").click()
    return page


@pytest.fixture
def authenticated_page(page: Page, auth_session: AuthSession) -> Page:
    context = page.context

    context.add_cookies(
        [
            {"name": "token", "value": auth_session.token, "url": BASE_URL},
            {"name": "welcomebanner_status", "value": "dismiss", "url": BASE_URL},
            {"name": "cookieconsent_status", "value": "dismiss", "url": BASE_URL},
            {"name": "language", "value": "en", "url": BASE_URL},
        ]
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
