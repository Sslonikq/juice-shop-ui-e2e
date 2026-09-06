import pytest
from playwright.sync_api import Page

from src.pages.home_page import HomePage


@pytest.mark.smoke
def test_storefront_shows_products(storefront: Page) -> None:
    HomePage(storefront).assert_products_visible()
