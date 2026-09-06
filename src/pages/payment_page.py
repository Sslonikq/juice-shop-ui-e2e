import allure
from playwright.sync_api import Page

from src.pages.order_summary_page import OrderSummaryPage


class PaymentPage:
    def __init__(self, page: Page) -> None:
        self._page = page

    @allure.step("Выбрать платёжную карту")
    def select_first_card(self) -> "PaymentPage":
        self._page.get_by_role("radio").first.check()
        return self

    @allure.step("Перейти к подтверждению заказа")
    def proceed(self) -> OrderSummaryPage:
        self._page.get_by_role("button", name="Proceed to review").click()
        return OrderSummaryPage(self._page)
