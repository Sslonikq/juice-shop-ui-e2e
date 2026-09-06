import pytest
from playwright.sync_api import Page

from src.pages.home_page import HomePage
from src.models.user import User


@pytest.mark.auth
def test_api_auth_bypass_opens_authenticated_session(
    authenticated_page: Page, registered_user: User
) -> None:
    HomePage(authenticated_page).header.assert_logged_in_as(registered_user.email)
