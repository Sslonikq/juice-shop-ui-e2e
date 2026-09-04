import pytest
from playwright.sync_api import Page, expect

from src.config.settings import BASE_URL
from src.models.user import User


@pytest.mark.auth
def test_login(storefront: Page, registered_user: User) -> None:
    page = storefront
    page.goto(f"{BASE_URL}/#/login")

    page.get_by_label("Text field for the login email").fill(registered_user.email)
    page.get_by_label("Text field for the login password").fill(registered_user.password)
    page.get_by_role("button", name="Login", exact=True).click()

    # Вход завершается редиректом; без ожидания клик по меню попадёт в
    # ещё анонимную страницу, и меню схлопнется при переходе.
    expect(page).to_have_url(f"{BASE_URL}/#/search")

    page.get_by_label("Show/hide account menu").click()
    account_menu = page.get_by_role("menu")
    expect(account_menu.get_by_text(registered_user.email)).to_be_visible()
