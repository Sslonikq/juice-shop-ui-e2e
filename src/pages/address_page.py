import allure
from playwright.sync_api import Page

from src.pages.delivery_page import DeliveryPage


class AddressPage:
    def __init__(self, page: Page) -> None:
        self._page = page

    @allure.step("Выбрать адрес доставки")
    def select_first_address(self) -> "AddressPage":
        self._page.get_by_role("radio").first.check()
        return self

    @allure.step("Перейти к выбору доставки")
    def proceed(self) -> DeliveryPage:
        self._page.get_by_role("button", name="Proceed to payment selection").click()
        return DeliveryPage(self._page)
