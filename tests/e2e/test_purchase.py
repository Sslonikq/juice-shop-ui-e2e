import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.purchase
def test_purchase(buyer_page: Page) -> None:
    page = buyer_page

    page.get_by_role("button", name="Add to Basket").first.click()
    expect(page.locator("simple-snack-bar")).to_contain_text("into basket")

    page.get_by_role("button", name="Show the shopping cart").click()
    page.get_by_role("button", name="Checkout").click()

    page.get_by_role("radio").first.check()
    page.get_by_role("button", name="Proceed to payment selection").click()

    page.get_by_role("radio").first.check()
    page.get_by_role("button", name="Proceed to delivery method selection").click()

    page.get_by_role("radio").first.check()
    page.get_by_role("button", name="Proceed to review").click()

    page.get_by_role("button", name="Complete your purchase").click()

    expect(page.get_by_text("Thank you for your purchase!")).to_be_visible()
