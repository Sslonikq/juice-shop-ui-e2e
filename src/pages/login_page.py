from playwright.sync_api import Page

from src.config.settings import BASE_URL
from src.pages.home_page import HomePage
from src.models.user import User



class LoginPage:
    def __init__(self, page: Page) -> None:
        self._page = page
        
    def open(self) -> "LoginPage":
        self._page.goto(f"{BASE_URL}/#/login")
        return self
        
    def login_as(self, user: User) -> HomePage:
        self._page.get_by_role("textbox", name="Text field for the login email").fill(user.email)
        self._page.get_by_role("textbox", name="Text field for the login password").fill(user.password)
        self._page.get_by_role("button", name="Login", exact=True).click()
        self._page.wait_for_url("**/#/search")
        return HomePage(self._page)
        
            