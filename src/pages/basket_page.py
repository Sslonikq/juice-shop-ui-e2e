from playwright.sync_api import Page

from src.pages.address_page import AddressPage


class BasketPage:
    def __init__(self, page: Page) -> None:
        self._page = page

    def checkout(self) -> AddressPage:
        self._page.get_by_role("button", name="Checkout").click()
        return AddressPage(self._page)
