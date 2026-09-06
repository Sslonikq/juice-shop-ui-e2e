import allure
import pytest
from playwright.sync_api import Page

from src.models.user import User
from src.pages.home_page import HomePage


@allure.feature("Авторизация")
@allure.title("Сессия устанавливается через API без формы логина")
@pytest.mark.auth
def test_api_auth_bypass_opens_authenticated_session(
    authenticated_page: Page, registered_user: User
) -> None:
    HomePage(authenticated_page).header.assert_logged_in_as(registered_user.email)
