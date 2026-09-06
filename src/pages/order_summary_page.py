import allure
from playwright.sync_api import Page

from src.pages.order_confirmation_page import OrderConfirmationPage


class OrderSummaryPage:
    def __init__(self, page: Page) -> None:
        self._page = page

    @allure.step("Оплатить заказ")
    def place_order(self) -> OrderConfirmationPage:
        self._page.get_by_role("button", name="Complete your purchase").click()
        return OrderConfirmationPage(self._page)
