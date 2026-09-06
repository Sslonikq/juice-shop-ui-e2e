import allure
from playwright.sync_api import Locator, Page, expect


class Header:
    def __init__(self, page: Page) -> None:
        self._page = page

    @allure.step("Открыть корзину из шапки")
    def open_basket(self) -> None:
        self._page.get_by_role("button", name="Show the shopping cart").click()

    @allure.step("Открыть меню аккаунта")
    def open_account_menu(self) -> Locator:
        self._page.get_by_role("button", name="Show/hide account menu").click()
        return self._page.get_by_role("menu")

    @allure.step("Проверить, что выполнен вход под {email}")
    def assert_logged_in_as(self, email: str) -> None:
        account_menu = self.open_account_menu()
        expect(account_menu.get_by_text(email)).to_be_visible()
