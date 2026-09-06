import pytest
from playwright.sync_api import Page

from src.models.user import User
from src.pages.login_page import LoginPage


@pytest.mark.auth
def test_login(storefront: Page, registered_user: User) -> None:
    home_page = LoginPage(storefront).open().login_as(registered_user)
    home_page.header.assert_logged_in_as(registered_user.email)
