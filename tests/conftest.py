from collections.abc import Iterator

import pytest
from playwright.sync_api import APIRequestContext, Page, Playwright

from src.api.api_client import ApiClient
from src.config.settings import BASE_URL
from src.factories.user_factory import UserFactory
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
def storefront(page: Page) -> Page:
    page.goto(BASE_URL)
    page.get_by_role("button", name="Close Welcome Banner").click()
    page.get_by_role("button", name="dismiss cookie message").click()
    return page
