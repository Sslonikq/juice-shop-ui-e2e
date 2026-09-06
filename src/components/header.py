from playwright.sync_api import Page


class Header:

    def __init__(self, page: Page) -> None:
        self._page = page

    def open_basket(self) -> None:
        self._page.get_by_role("button", name="Show the shopping cart").click()
