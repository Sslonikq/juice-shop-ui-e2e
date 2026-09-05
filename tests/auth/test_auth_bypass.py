import pytest
from playwright.sync_api import Page, expect

from src.models.user import User


@pytest.mark.auth
def test_api_auth_bypass_opens_authenticated_session(
    authenticated_page: Page, registered_user: User
) -> None:
    page = authenticated_page
    page.get_by_label("Show/hide account menu").click()

    account_menu = page.get_by_role("menu")
    expect(account_menu.get_by_text(registered_user.email)).to_be_visible()

