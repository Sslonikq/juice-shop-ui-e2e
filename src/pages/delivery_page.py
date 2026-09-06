import allure
from playwright.sync_api import Page

from src.pages.payment_page import PaymentPage


class DeliveryPage:
    def __init__(self, page: Page) -> None:
        self._page = page

    @allure.step("Выбрать способ доставки")
    def select_first_delivery_method(self) -> "DeliveryPage":
        self._page.get_by_role("radio").first.check()
        return self

    @allure.step("Перейти к выбору способа оплаты")
    def proceed(self) -> PaymentPage:
        self._page.get_by_role(
            "button", name="Proceed to delivery method selection"
        ).click()
        return PaymentPage(self._page)
