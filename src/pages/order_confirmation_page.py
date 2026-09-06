import allure
from playwright.sync_api import Page, expect


class OrderConfirmationPage:
    def __init__(self, page: Page) -> None:
        self._page = page

    @allure.step("Проверить, что заказ оформлен")
    def assert_order_created(self) -> None:
        expect(self._page.get_by_text("Thank you for your purchase!")).to_be_visible()
