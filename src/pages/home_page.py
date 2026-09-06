from playwright.sync_api import Page, expect

from src.components.header import Header
from src.components.toast import Toast
from src.pages.basket_page import BasketPage


class HomePage:
    def __init__(self, page: Page) -> None:
        self._page = page
        self.header = Header(page)
        self.toast = Toast(page)

    def add_first_product_to_basket(self) -> "HomePage":
        self._page.get_by_role("button", name="Add to Basket").first.click()
        self.toast.wait_for_message("into basket")
        return self

    def open_basket(self) -> BasketPage:
        self.header.open_basket()
        return BasketPage(self._page)

    def assert_products_visible(self) -> None:
        products = self._page.get_by_role("button", name="Add to Basket")
        expect(products.first).to_be_visible()
