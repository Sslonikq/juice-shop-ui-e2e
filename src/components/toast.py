from playwright.sync_api import Page, expect


class Toast:

    def __init__(self, page: Page) -> None:
        self._page = page

    def wait_for_message(self, text: str) -> None:
        snack_bar = self._page.locator("simple-snack-bar")
        expect(snack_bar).to_contain_text(text)
