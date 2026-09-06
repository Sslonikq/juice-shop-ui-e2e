import allure
from playwright.sync_api import Page

from src.config.settings import BASE_URL
from src.models.user import User
from src.pages.home_page import HomePage


class LoginPage:
    def __init__(self, page: Page) -> None:
        self._page = page

    @allure.step("Открыть страницу логина")
    def open(self) -> "LoginPage":
        self._page.goto(f"{BASE_URL}/#/login")
        return self

    @allure.step("Войти под тестовым пользователем")
    def login_as(self, user: User) -> HomePage:
        email_field = self._page.get_by_role(
            "textbox", name="Text field for the login email"
        )
        password_field = self._page.get_by_role(
            "textbox", name="Text field for the login password"
        )
        email_field.fill(user.email)
        password_field.fill(user.password)
        self._page.get_by_role("button", name="Login", exact=True).click()
        self._page.wait_for_url("**/#/search")
        return HomePage(self._page)
