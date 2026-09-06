import allure
import pytest
from playwright.sync_api import Page

from src.pages.home_page import HomePage


@allure.feature("Витрина")
@allure.title("Каталог товаров загружается и доступен покупателю")
@pytest.mark.smoke
def test_storefront_shows_products(storefront: Page) -> None:
    HomePage(storefront).assert_products_visible()
