import pytest
from playwright.sync_api import Page, expect

from src.config.settings import BASE_URL


@pytest.mark.smoke
def test_storefront_shows_products(page: Page) -> None:
    page.goto(BASE_URL)

    page.get_by_role("button", name="Close Welcome Banner").click()
    page.get_by_role("button", name="dismiss cookie message").click()

    expect(page.get_by_role("button", name="Add to Basket").first).to_be_visible()
